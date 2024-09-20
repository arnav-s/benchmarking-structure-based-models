# Exploring zero-shot structure-based protein fitness prediction
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.13819824.svg)](https://doi.org/10.5281/zenodo.13819824)

This is a repository of code needed to replicate benchmarks of structure based models in ProteinGym

## Table of Contents
  * [Setup](#setup)
    * [Conda environment](#conda)
  * [Accessing Data](#access_data)

## Setup
### Conda environment setup
The conda environment can be setup using 
```
  conda env create -f environment.yml
```
### SSEmb setup
You can follow the instructions on:

### ProteinGym setup

## Accessing Data:

### ProteinGym Data:
Get zero-shot scores:
```
wget https://marks.hms.harvard.edu/proteingym/zero_shot_substitutions_scores.zip
```
These scores can be extracted to the location of your choosing and then each script can be pointed to this location.

### Generated Data:
Data to run experiments can be found in our [Zenodo repository](https://doi.org/10.5281/zenodo.13819824).

  * `experimental_struct_artifacts` contains the experimentally determined structures
for ProteinGym assays used in our analysis along with the reference file needed to
generate ESM inverse folding predictions for these structures in ProteinGym.
  * `results` contains the prediction results obtained by running SSEmb on the 216
ProteinGym assays being considered in this study.
  * `test.tar.gz` contains all the structures from ProteinGym as well as MSAs generated
using mmseqs2. To use this directory:
    * Setup SSEmb as directed in its [repository](https://github.com/KULL-Centre/_2023_Blaabjerg_SSEmb)
    * Download this file and extract it in the data folder.

