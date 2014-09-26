#!/usr/bin/env python
from __future__ import unicode_literals
from confu import atlas

from troposphere import (
    Template, FindInMap, GetAtt, Ref, Parameter, Join, Base64, Select, Output,
    ec2 as ec2
)


template = Template()

template.add_description('LogServer')

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
