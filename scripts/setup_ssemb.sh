#! /bin/bash

set -e

DIRECTORY="_2023_Blaabjerg_SSEmb"

if [ -d "$DIRECTORY" ]; then
    echo "Repository already exists."
else
    git clone https://github.com/KULL-Centre/_2023_Blaabjerg_SSEmb.git
fi

if [ ! -f assets/test.tar.gz ]; then
    echo "Couldn't find file in repo root folder."
    echo "Please download test.tar.gz from the Zenodo repository and place it in the assets directory of this project."
fi
cd assets
tar -xvzf test.tar.gz 
cd ..
cp -r assets/test/ _2023_Blaabjerg_SSEmb/data/
rm -rf assets/test
