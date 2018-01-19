#!/bin/bash

for node in {0..1} {3..8}
do

    echo "Testing directory access on on node ${node}..."
    ssh pacifix${node} "cd /beegfsPACIFIX;\
    df . -H; \
    rm config.conf; \
    touch config.conf;" 
 
done
