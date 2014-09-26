# infra-log

Does these things:

- log server

Setup as usual:

```bash
$ git clone --recursive git@github.com:balanced-cookbooks/infra-global.git
$ cd infra-log
$ mkvirtualenv infra-log
(infra-global)$ pip install -r requirements.txt 
```

## Local development

(infra-nat)$ vagrant up

## Build and publish config

NOTE: You must do this on a machine with the same architecture as what you're about to deploy to.

If you are on OSX run the following commands

```bash
(infra-nat)$ pypi_username=user pypi_password=pass vagrant provision infra-log
(infra-nat)$ vagrant ssh -c "source ~/infra/bin/activate && cd ~/infra-log/ && confu pkg clean && confu pkg build"
(infra-nat)$ confu pkg archive
```

to see what we've released:

```bash
(infra-nat)$ confu pkg archived
```


## Launch a stack

```bash
$ confu cfn create formations/log.py ConfVer=f26fa6d KeyName=your-aws-ssh-key-name
```


## Update a stack

```bash
$ confu cfn update test-log-bi1dmz formations/log.py KeyName=mj-mbpro-may-2014 ConfVer=da37796 DesiredCapacity=2 MaxSize=3
```

## Re-run the playbook on the stack

```bash
$ ansible-playbook -i inventories/poundpay site.yml
```

## Debugging

```bash
$ echo '{"channel": "balanced-integration.debug.test", "payload": {"x": 10}}' >> /var/log/td-agent/debug.log
```

where `channel` is the routing key you want to use.
