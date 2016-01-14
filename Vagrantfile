ANSIBLE_GROUPS = {
              "masternodes" => ["node1"],
              "slavenodes" => ["node2", "node3"],
              "all_groups:children" => ["masternodes", "slavenodes"]
            }

Vagrant.configure(2) do |config|

  config.vm.box = "ubuntu/trusty64"
  config.vm.synced_folder '.', '/vagrant', nfs: true

  config.vm.define "node1" do |node1|
      node1.vm.network "private_network", ip: "192.168.8.100"
      node1.vm.hostname = "rancher-server"
      node1.vm.provider "virtualbox" do |v|
        v.customize ["modifyvm", :id, "--memory", "924"]
        v.customize ["modifyvm", :id, "--cpus", "1"]
      end
      node1.vm.provision "ansible" do |ansible|
        ansible.playbook = "playbook.yml"
        ansible.groups = ANSIBLE_GROUPS
      end
  end

  config.vm.define "node2" do |node2|
      node2.vm.network "private_network", ip: "192.168.8.101"
      node2.vm.hostname = "rancher-slave1"
      node2.vm.provider "virtualbox" do |v|
         v.customize ["modifyvm", :id, "--memory", "1024"]
         v.customize ["modifyvm", :id, "--cpus", "2"]
      end
      node2.vm.provision "ansible" do |ansible|
        ansible.playbook = "playbook.yml"
        ansible.groups = ANSIBLE_GROUPS
      end
  end

  config.vm.define "node3" do |node3|
      node3.vm.network "private_network", ip: "192.168.8.102"
      node3.vm.hostname = "rancher-slave2"
      node3.vm.provider "virtualbox" do |v|
        v.customize ["modifyvm", :id, "--memory", "1024"]
        v.customize ["modifyvm", :id, "--cpus", "2"]
      end
      node3.vm.provision "ansible" do |ansible|
        ansible.playbook = "playbook.yml"
        ansible.groups = ANSIBLE_GROUPS
      end
  end

end
