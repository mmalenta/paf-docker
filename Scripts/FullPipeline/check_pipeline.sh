#!/bin/bash

for node in {0..8}
do

    echo "Searching for paf-docker instances on pacifix${node}..."
    ssh pacifix${node} "docker ps -f name=paf-; "
 
done
