# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "bento/ubuntu-16.04"

  config.vm.box_check_update = false
  config.ssh.insert_key = false
  config.vm.network "private_network", ip: "192.168.50.4"
  config.vm.network "private_network", ip: "192.168.50.5"
  # Forward Trex Ports
  config.vm.network "forwarded_port", guest: 4500, host: 4500
  config.vm.network "forwarded_port", guest: 4501, host: 4501

  config.vm.provider "virtualbox" do |vb|
    vb.customize ["modifyvm", :id, "--nicpromisc2", "allow-all"]
    vb.customize ["modifyvm", :id, "--nicpromisc3", "allow-all"]
    vb.memory = "2048"
    vb.cpus = 4
  end

  config.vm.provision "shell", inline: <<-SHELL
     apt-get update
     apt-get -y install tcpdump python-pip
     wget --no-cache http://trex-tgn.cisco.com/trex/release/v2.30.tar.gz
     tar xvzf v2.30.tar.gz
     mv v2.30 /opt/trex
     cd /opt/trex
     tar xvzf trex_client_v2.30.tar.gz
     ./dpdk_setup_ports.py -c enp0s8 enp0s9 -o /etc/trex_cfg.yaml
  SHELL
end
