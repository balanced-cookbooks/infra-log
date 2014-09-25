# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  # All Vagrant configuration is done here. The most common configuration
  # options are documented and commented below. For a complete reference,
  # please see the online documentation at vagrantup.com.

  project_name = File.basename(Dir.getwd)

  # Every Vagrant virtual environment requires a box to build off of.
  config.vm.box = "precise64"
  config.hostmanager.enabled = true # Must install: vagrant plugin install vagrant-hostmanager

  config.vm.define project_name do |node|
    node.vm.network :private_network, :ip => '10.20.1.10'
    config.vm.synced_folder '.', "/home/vagrant/#{project_name}"
    config.vm.provision :ansible do |ansible|
      ansible.playbook       = './provisioning/build.yml'
      ansible.inventory_path = './provisioning/inventory'
      ansible.host_key_checking = false
      ansible.extra_vars     = {
          ansible_ssh_user: 'vagrant',
          sudo: true
      }
    end

  end

  config.vm.define 'log.server1' do |node|
    node.vm.network :private_network, :ip => '10.20.2.11'
    config.vm.host_name = 'log.server1'
  end

  config.vm.define 'log.server2' do |node|
    node.vm.network :private_network, :ip => '10.20.2.12'
    config.vm.host_name = 'log.server2'
  end

  config.vm.define 'log.client1' do |node|
    node.vm.network :private_network, :ip => '10.20.2.21'
    config.vm.host_name = 'log.client1'
  end

  config.vm.provision :ansible do |ansible|
    ansible.playbook = './vagrant-ansible.yml'
    ansible.extra_vars = {
        ansible_ssh_user: 'vagrant',
        sudo: true
    }
    ansible.host_key_checking = false
    ansible.groups = {
        'fluentd-servers' => ['log.server1', 'log.server2'],
        'fluentd-clients' => ['log.client1'],
    }

    # Debugging helpers
    #ansible.verbose = 'vvvv'
    #ansible.hosts = 'all'
  end

end
