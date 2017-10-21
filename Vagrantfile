# -*- mode: ruby -*-
# vi: set ft=ruby :
#
require "vagrant-host-shell"
require "vagrant-junos"

Vagrant.configure("2") do |config|
  config.vm.box_check_update = false
  config.ssh.insert_key = false

  # Trex VM
  config.vm.define "trex", primary: true do |trex|
      trex.vm.box = "bento/ubuntu-16.04"

      trex.vm.network "private_network", ip: "192.168.50.4",
          virtualbox__intnet: "net1"
      trex.vm.network "private_network", ip: "192.168.60.4",
          virtualbox__intnet: "net2"
      # Forward Trex Ports
      trex.vm.network "forwarded_port", guest: 4500, host: 4500
      trex.vm.network "forwarded_port", guest: 4501, host: 4501

      trex.vm.provider "virtualbox" do |vb|
        vb.customize ["modifyvm", :id, "--nicpromisc2", "allow-all"]
        vb.customize ["modifyvm", :id, "--nicpromisc3", "allow-all"]
        vb.memory = "2048"
        vb.cpus = 4
      end

      trex.vm.provision "shell", inline: <<-SHELL
         apt-get update
         apt-get -y install tcpdump python-pip tmux
         wget --no-cache http://trex-tgn.cisco.com/trex/release/v2.30.tar.gz
         tar xvzf v2.30.tar.gz
         mv v2.30 /opt/trex
         cd /opt/trex
         tar xvzf trex_client_v2.30.tar.gz
         ./dpdk_setup_ports.py -c enp0s8 enp0s9 -o /etc/trex_cfg.yaml --ips 192.168.50.4 192.168.60.4 --def-gws 192.168.50.5 192.168.60.5
      SHELL
   end
  # DUT VM
  config.vm.define "dut" do |dut|
      dut.vm.box = "juniper/ffp-12.1X47-D15.4-packetmode"
      dut.vm.network "private_network", ip: "192.168.50.5",
          virtualbox__intnet: "net1"
      dut.vm.network "private_network", ip: "192.168.60.5",
          virtualbox__intnet: "net2"

      dut.vm.provider "virtualbox" do |vb|
        vb.customize ["modifyvm", :id, "--nicpromisc2", "allow-all"]
        vb.customize ["modifyvm", :id, "--nicpromisc3", "allow-all"]
        vb.memory = "2048"
        vb.cpus = 4
      end

   end

end
