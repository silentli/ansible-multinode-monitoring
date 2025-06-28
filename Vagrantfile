# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  # Use Ubuntu 22.04 LTS as base image
  config.vm.box = "ubuntu/jammy64"

  # Disable automatic box update checking
  config.vm.box_check_update = false

  # Create Node 1 - Mock Service Node
  config.vm.define "app-node" do |node1|
    node1.vm.hostname = "node1"
    node1.vm.network "private_network", ip: "192.168.56.11"
    
    node1.vm.provider "virtualbox" do |vb|
      vb.name = "ansible-multinode-node1"
      vb.memory = "1024"
      vb.cpus = 1
      vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
    end
  end

  # Create Node 2 - Database Node
  config.vm.define "db-node" do |node2|
    node2.vm.hostname = "node2"
    node2.vm.network "private_network", ip: "192.168.56.12"
    
    node2.vm.provider "virtualbox" do |vb|
      vb.name = "ansible-multinode-node2"
      vb.memory = "1024"
      vb.cpus = 1
      vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
    end
  end

  # Create Node 3 - Monitoring Node
  config.vm.define "monitor-node" do |node3|
    node3.vm.hostname = "node3"
    node3.vm.network "private_network", ip: "192.168.56.13"
    
    node3.vm.provider "virtualbox" do |vb|
      vb.name = "ansible-multinode-node3"
      vb.memory = "2048"
      vb.cpus = 2
      vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
    end
  end

  # Common configuration for all VMs
  config.vm.provider "virtualbox" do |vb|
    vb.gui = false
    vb.linked_clone = true
  end

  # Sync the ansible directory to all VMs
  config.vm.synced_folder ".", "/vagrant", disabled: false
end
