#! /bin/bash

DIRECTORY="_2023_Blaabjerg_SSEmb"

if [ -d "$DIRECTORY" ]; then
    echo "Repository already exists."
else
    git clone https://github.com/KULL-Centre/_2023_Blaabjerg_SSEmb.git
fi

if [ ! -f test.tar.gz ]; then
    echo "Couldn't find file in repo root folder."
    echo "Please download test.tar.gz from the Zenodo repository and place it in the root directory of this project."
fi

tar -xvzf test.tar.gz && cp -r test/ _2023_Blaabjerg_SSEmb/data/
