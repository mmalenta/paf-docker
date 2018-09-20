#!/bin/bash

for node in {0..8}
do

    echo "Killing paf docker on pacifix${node}..."
    ssh pacifix${node} "docker kill paf-pipeline-0 paf-pipeline-1 paf-heimdall-0 paf-heimdall-1;"
 
done
