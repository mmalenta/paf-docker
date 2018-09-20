#!/bin/bash

canddir=$1
datadir=$2
nthreads=$3

for thread in $(seq 1 $nthreads)
do
    echo "Launching thread ${thread}"
    python /beegfs/PAFJAN/heimdall/proc_multi.py ${canddir} ${datadir} ${thread} ${nthreads} &
    sleep 1
done
