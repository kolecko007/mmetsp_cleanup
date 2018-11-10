```
 __  __ __  __ ______ _______ _____ _____     _____ _      ______          _   _ _    _ _____
 |  \/  |  \/  |  ____|__   __/ ____|  __ \   / ____| |    |  ____|   /\   | \ | | |  | |  __ \
 | \  / | \  / | |__     | | | (___ | |__) | | |    | |    | |__     /  \  |  \| | |  | | |__) |
 | |\/| | |\/| |  __|    | |  \___ \|  ___/  | |    | |    |  __|   / /\ \ | . ` | |  | |  ___/
 | |  | | |  | | |____   | |  ____) | |      | |____| |____| |____ / ____ \| |\  | |__| | |
 |_|  |_|_|  |_|______|  |_| |_____/|_|       \_____|______|______/_/    \_|_| \_|\____/|_|
```

# Installation

The deployed and prepared environment for running MMETSP cleanup iside the virtual machine.

## Requirements
- 150 GB of free space
- 20+ Gb of RAM


## Preparation (examples are for the Ubuntu)

1) install virtualbox:
```console
$ sudo apt-get install virtualbox
```

2) install vagrant:
```console
$ sudo apt-get install vagrant
```

3) install vagrant disksize plugin:
```console
$ vagrant plugin install vagrant-disksize
```

4) Create an empty folder and download the preparation shell script into it:
```console
$ wget http://nenarokov.com/mmetsp_cleanup/download_box.sh
```

5) Make the script executable and run it
```console
$ chmod +x download_box.sh
$ ./download_box.sh
```

This script downloads all necessary files for the virtual machine (~25 Gb).

6) add the box to the vagrant environment
```console
$ vagrant box add mmetsp_cleanup mmetsp_cleanup.box
```

7) start the virtual machine
```console
$ vagrant up
```

# How to use
When virtual machine is ready you can connect to it using ssh:
```console
$ vagrant ssh
```

Main configuration files for editing:
`/home/vagrant/mmetsp_data/settings.yml` - coverage_ratio thresholds are defined there
`/home/vagrant/mmetsp_data/types.csv` - types and thresholds for all possible dataset combinations

In the WM home folder, you will find a script run.sh, which starts the mmetsp cleanup pipeline.
To run the process simply run that script:
```console
$ ./run.sh
```

The results will appear in the folder: `/home/vagrant/mmetsp_data/results/`

## Tips
To exit the virtual machine terminal session type
```console
$ exit
```

To stop running virtual machine from your local computer type the command
```console
$ vagrant halt
```

To view the status of VM type
```console
$ vagrant status
```

You can share files between VM and local computer by putting them to the folder with Vagrantfile.
They will appear in the VM in /vagrant folder.
It can be useful if you don't want to edit types.csv and settings.csv from the VM.

## Contact
Email me and I can solve your problems and answer your questions:
serafim.nenarokov@gmail.com

---

# :construction: Preparation pipeline (for internal purposes only)

## First of all: check and fix names

### check_datasets.rb
Receives a path to the dataset folder with all the `.fas` files (`--datasets_path`).

Checks if the file name and MMETSP name of contigs are equal.

As a result builds a `wrong_names.csv` file with the structure: `file_name,name_of_contigs`.

Also the scripts assures that all the contigs belong to the same MMETSP sample.

### fix_datasets.rb
Receives a path to the `wrong_names.csv` file (`--wrong_names_path`) and a path to the datasets folder (`--datasets_path`).

In each file with a wrong contig name script replaces the MMETSP name of contigs with a name from file name.

### fix_one_vs_all.rb
Replaces all the occurrences of "wrong names" in each one vs all `.blastab` file.

### fix_all_vs_all.rb
Replaces all the occurrences of "wrong names" in each all vs all `.blastab` file.

### check_hits.rb
Checks, if files in folder provided contain wrong names.

### Archive all the data
```
tar cvf datasets.tar.gz datasets/*.blastab
tar cvf one_vs_all.tar.gz one_vs_all/*.blastab
tar cvf all_vs_all.tar.gz all_vs_all/*.blastab
```

## Preparation

### prepare.rb

Receives the three .tar archives with:
- datasets (`.fas` files)
- one vs all hits (`.blastab`)
- all vs all BLAST hits (`.blastab`)

As an output makes a prepared structure of Decross project.

## Make a coverage database
#TODO
