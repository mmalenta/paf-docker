#!/bin/bash

for node in {0..8}
do

    echo "Killing DADA buffers docker on pacifix${node}..."
    ssh pacifix${node} "bash -s" < run_dada.sh
 
done
