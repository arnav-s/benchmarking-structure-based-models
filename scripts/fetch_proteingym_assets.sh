#!/bin/bash

if [ ! -d assets ]; then
    mkdir assets
fi

#Fetch reference files
wget -O assets/DMS_substitutions_ref_file.csv https://raw.githubusercontent.com/OATML-Markslab/ProteinGym/main/reference_files/DMS_substitutions.csv

# Fetch benchmark score file
wget -O assets/DMS_substitutions_Spearman_DMS_level.csv https://raw.githubusercontent.com/OATML-Markslab/ProteinGym/main/benchmarks/DMS_zero_shot/substitutions/Spearman/DMS_substitutions_Spearman_DMS_level.csv
