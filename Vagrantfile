Vagrant.configure("2") do |config|
  config.vm.box = "bento/ubuntu-16.04"

  config.vm.provider :virtualbox do |vb|
    vb.customize [
      "modifyvm", :id,
      "--cpuexecutioncap", "100", # CPU usage limit (in %)
      "--memory", "2048",         # RAM limit (in MB)
    ]
  end

  config.vm.provision "shell", path: "setup.sh"
end
