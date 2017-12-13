#!/bin/bash

for node in {0..1} 
do

    node0=$((2 * $node));
    node1=$((2 * $node + 1));
    echo "Testing directory access on on node ${node}..."
    ssh pacifix${node} "cd /media/beegfs/11_12_2017/0329;\
    rm 2017*.fil
    python /home/pulsar/soft/paf-docker/paf/merge.py -d /media/beegfs/11_12_2017/0329 -b ${node0}
    python /home/pulsar/soft/paf-docker/paf/merge.py -d /media/beegfs/11_12_2017/0329 -b ${node1}"
   
 
done

for node in {3..7} 
do

    node0=$((2 * $node - 2));
    node1=$((2 * $node + 1 - 2));
    echo "Testing directory access on on node ${node}..."
    ssh pacifix${node} "cd /media/beegfs/11_12_2017/0329;\
    rm 2017*.fil
    python /home/pulsar/soft/paf-docker/paf/merge.py -d /media/beegfs/11_12_2017/0329 -b ${node0}
    python /home/pulsar/soft/paf-docker/paf/merge.py -d /media/beegfs/11_12_2017/0329 -b ${node1}"


done

