#! /bin/bash

set -e

DIRECTORY="ProteinGym"

if [ -d "$DIRECTORY" ]; then
    echo "Repository already exists."
else
    git clone https://github.com/OATML-Markslab/ProteinGym.git
fi

if [ ! -f assets/experimental_structs_artifacts.tar.gz ]; then
    echo "Couldn't find file in repo root folder."
    echo "Please download experimental_structs_artifacts.tar.gz from the Zenodo repository and place it in the assets directory of this project."
fi
cd assets
tar -xvzf experimental_structs_artifacts.tar.gz
cd ..
mv assets/experimental_structs_artifacts/compute_fitness_esm_if1.py ProteinGym/proteingym/baselines/esm/compute_fitness_esm_if1.py
mv assets/experimental_structs_artifacts/score_multichain_structs_esm.sh ProteinGym/scripts/scoring_DMS_zero_shot/score_multichain_structs_esm.sh
mv assets/experimental_structs_artifacts/scoring_ESM_IF1_multichain_substitutions.sh ProteinGym/scripts/scoring_DMS_zero_shot/scoring_ESM_IF1_multichain_substitutions.sh
mv assets/experimental_structs_artifacts/DMS_substitutions_hetero.csv ProteinGym/reference_files/DMS_substitutions_hetero.csv
mkdir ProteinGym/proteingym/baselines/esm/model_checkpoints/


