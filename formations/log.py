#!/usr/bin/env python
from __future__ import unicode_literals
from confu import atlas

from troposphere import (
    Template, FindInMap, GetAtt, Ref, Parameter, Join, Base64, Select, Output,
    ec2 as ec2, If
)


template = Template()

template.add_description('LogServer')

template.add_parameter([
    Parameter(
        'DataDevice',
        Description='Data device',
        Type='String',
        Default='/dev/xvdf',
    ),
    Parameter(
        'DataIops',
        Description='Number of provisioned data IOPS',
        Type='Number',
        Default='0',
    ),
    Parameter(
        'DataSize',
        Description='Size of data device in GB',
        Type='Number',
        Default='500',
    ),
])

template.add_condition('EnableDataIops', {
    'Fn::Not': [{'Fn::Equals':  [Ref('DataIops'), 0]}]
})

atlas.infra_params(template)  ## ssh_key, Env, Silo

atlas.conf_params(template)   ## Conf Name, Conf Version, Conf tarball bucket

atlas.instance_params(
    template,
    roles_default=['log', ],
    iam_default='log',
)

atlas.scaling_params(template)

atlas.mappings(
    template,
    accounts=[atlas.poundpay],
)

sg = atlas.instance_secgrp(
    template,
    name='Log',
)

for proto in ('tcp', 'udp'):
    template.add_resource(ec2.SecurityGroupIngress(
        'FluentD' + proto.upper(),
        GroupId=Ref(sg),
        CidrIp=atlas.vpc_cidr,
        FromPort='24224',
        ToPort='24224',
        IpProtocol=proto,
    ))

i_meta_data = {}
atlas.cfn_auth_metadata(i_meta_data)
atlas.cfn_init_metadata(i_meta_data)

# mount a drive to /mnt/logs
devices = i_meta_data['AWS::CloudFormation::Init'].get('devices', {})
devices['commands'] = {
    'data-1': {
        'command': Join(
            ' ', [
                'mkdir -p /mnt/logs', '&&',
                'mkfs.xfs', Ref('DataDevice'),
                '&&',
                'echo "', Ref('DataDevice'),
                    '/mnt/logs xfs defaults,noatime 0 0" >> /etc/fstab',
                '&&',
                # micro instances do not have ephemeral drive so we need to
                # ignore any mounting errors
                '(mount -a || true)',
                '&&',
                'chmod 775 /mnt/logs'
            ]
        )
    },
}
i_meta_data['AWS::CloudFormation::Init']['devices'] = devices
i_meta_data['AWS::CloudFormation::Init']['configSets']['default'].insert(
    0, 'devices'
)

i_user_data = Join(
    '',
    atlas.user_data('LogLaunchConfiguration') +
    atlas.user_data_signal_on_scaling_failure(),
)

i_launchconf = atlas.instance_launchconf(
    template,
    'Log',
    UserData=Base64(i_user_data),
    Metadata=i_meta_data,
    SecurityGroups=[Ref(sg)],
    BlockDeviceMappings=[
        ec2.BlockDeviceMapping(
            DeviceName=Ref('DataDevice'),
            Ebs=ec2.EBSBlockDevice(
                DeleteOnTermination=True,
                VolumeType=If('EnableDataIops', 'io1', 'standard'),
                Iops=If(
                    'EnableDataIops',
                    Ref('DataIops'),
                    Ref('AWS::NoValue')
                ),
                VolumeSize=Ref('DataSize'),
            ),
        ),
    ],
)

scaling_group = atlas.instance_scalegrp(
    template,
    'Log',
    LaunchConfigurationName=Ref(i_launchconf),
    MinSize=Ref('MinSize'),
    MaxSize=Ref('MaxSize'),
    DesiredCapacity=Ref('DesiredCapacity'),
)

if __name__ == '__main__':
    print template.to_json(indent=4, sort_keys=True)
