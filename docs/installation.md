---
layout: default
title: Installation
nav_order: 3
---

<div style="text-align: center;">
    <img src="assets/mnemosyne.png" width="900" alt="Mnemosyne on a computer" class="center">
</div>


# Installation Instructions

This is a python project but it does have a few non-python dependencies. I have created an `environment.yaml` file 
that would make the installation process a little bit easier I hope. This `yaml` file may change in the future as 
we add more functionalities. 

## Installing Conda

This one is fairly straightforward, you can follow the instructions [here](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) after
running the installation script you should be able to activate/deactivate conda environments. If you are installing this under some HPC environment, 
I suggest that you move the location of your conda cache to a different location. You can do that by following the instructions 
[here](https://docs.conda.io/projects/conda/en/stable/user-guide/configuration/custom-env-and-pkg-locations.html), the other option
is that you can create a [symbolic link](https://stackoverflow.com/questions/1951742/how-can-i-symlink-a-file-in-linux) to your `.cache`, 
`.singularity` and `.conda` folders in your `~` where the actual folders are in a partition with more storage. 

## Installing ccm_benchmate dependencies

Here are the instructions for installation. 

```bash
git clone https://github.com/celalp/mynemosine

# go into the directory
cd mynemosine

#create the conde env
conda env create -f environment.yaml #this might take a minute or 2
conda activate mynemosine

# install the python dependencies
pip install -r requirements.txt

pip install . 
```


This will create the conda environment and install all the dependencies. There are a few things to keep in mind which are 
not included in this package yet and there are some gotchas the main one being you will need postgresql database with 
pgvector extension enables, while you can install postgres with conda, the version of pgvector extension in conda is woefully out of date. 

We will create better instructions for this feature when it's ready to be tested. 

Please create an issue with all the error messages if you run into issues. 