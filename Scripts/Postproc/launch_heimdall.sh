#!/bin/bash

for node in {0..8} 
do
    echo "Starting job on node ${node}..."
    ssh pacifix${node} "/usr/bin/env OBSID=$obsid TOBS=$tobs  bash -s" < run_heimdall.sh > heimdall.launch.${node}.log &
done

