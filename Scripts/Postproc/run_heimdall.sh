#!/bin/bash

node=$( hostname | sed 's/pacifix\([0-9]*\)/\1/' )

for half in {0..1} ; do

   beam=$((2*node + half))
   echo "Processing beam ${beam} on ${node}:${half}"
   nvidia-docker run -u 50000:50000 -d --rm --net=host --name paf-heimdall-${half} -v /beegfs/PAFJAN/output/:/data/ -v /beegfs/PAFJAN/heimdall/:/output/ --ulimit memlock=-1 paf-heimdall /usr/bin/env gpu=$half beam=$beam /bin/bash -c '/output/process.sh $beam $gpu'
done


