#!/bin/bash

for node in {0..1} {3..7}
do

    echo "Testing directory access on on node ${node}..."
    ssh pacifix${node} "cd /media/beegfs/;\
    df . -H; \
    rm config.conf; \
    touch config.conf;" 
 
done
