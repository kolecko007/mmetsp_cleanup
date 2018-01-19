# MMETSP cleanup

## Installation

Download and install the [VirtualBox](https://www.virtualbox.org/wiki/Downloads) for your operating system.

Download the VirtualBox image by the [link](http://google.com).

Import the image and run the machine.

Open the terminal.

Type `./find_contaminations.py`

...

#TODO more detailed description

## :construction: Preparation pipeline (for internal purposes only)

Receives the three .tar archives with:
- datasets (`.fas` files)
- one vs all hits (`.blastab`)
- all vs all BLAST hits (`.blastab`)

As an output makes a prepared structure of Decross project.

### Check and fix names

#### check_datasets.rb
Receives a path to the dataset folder with all the `.fas` files (`--datasets_path`).

Checks if the file name and MMETSP name of contigs are equal.

As a result builds a `wrong_names.csv` file with the structure: `file_name,name_of_contigs`.

Also the scripts assures that all the contigs belong to the same MMETSP sample.

#### fix_datasets.rb
Receives a path to the `wrong_names.csv` file (`--wrong_names_path`) and a path to the datasets folder (`--datasets_path`).

In each file with a wrong contig name script replaces the MMETSP name of contigs with a name from file name.

#### fix_one_vs_all.rb
Replaces all the occurrences of "wrong names" in each one vs all `.blastab` file.

#### fix_all_vs_all.rb
Replaces all the occurrences of "wrong names" in each all vs all `.blastab` file.

#### Archive all the data
```
tar cvf datasets.tar.gz datasets/*.blastab
tar cvf one_vs_all.tar.gz one_vs_all/*.blastab
tar cvf all_vs_all.tar.gz all_vs_all/*.blastab
```

### Run preparation
#TODO

### Make a coverage database
#TODO
