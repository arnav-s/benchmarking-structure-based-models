# benchmarking-structure-based-models
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.13819824.svg)](https://doi.org/10.5281/zenodo.13819824)

This is a repository of code needed to replicate benchmarks of structure based models in ProteinGym

## Table of Contents
  * [Setup](#setup)
  * [Accessing Data](#access_data)

## Setup
  The conda environment can be setup using 
  ```
    conda env create -f environment.yml
  ```

## Accessing Data:

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
