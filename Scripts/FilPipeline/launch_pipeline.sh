#!/bin/bash

# this will be the observation ID used in this run
obsid=`date -u +%Y-%m-%d_%H%M%S`
tobs=300
if [[ -n "$1" ]] ; then
	tobs=$1
fi

echo "OBSID=$obsid TOBS=$tobs"

rm pafinder.launch.*.log
# Nodes 0,1,3-8 have two beams. Node 2 currently has a bad NIC and can only take 1 beam.
for node in {0..8} 
#for node in 0
do
    echo "Starting job on node ${node}..."
    ssh pacifix${node} "/usr/bin/env OBSID=$obsid TOBS=$tobs HALVES='0 1' bash -s" < run_this.sh > pafinder.launch.${node}.log &
done

# Make node 2 a special case MJK 2018-01-19
#node=2
#echo "Starting job on node ${node}..."
#ssh pacifix${node} "/usr/bin/env OBSID=$obsid TOBS=$tobs HALVES='1' bash -s" < run_this.sh > pafinder.launch.${node}.log &

wait
tail pafinder.launch.*.log

        #nvidia-docker run --rm -d --net=host -v /media/beegfs/:/beegfs/ --ulimit memlock=8589934592 paf-new /bin/bash -c 'for rep in $(seq 1 ${reps}); do mkdir ${directory}/${rep} -p; touch ${directory}/${rep}/run_${numa}_${rep}; done'"
        #numactl --membind ${numa} --cpunodebind ${numa} /pafinder/bin/pafinder --config /beegfs/config.conf -o ${directory}/${rep} -r 300 -v --numa ${numa} &> ${directory}/${rep}/run_${numa}_${rep}.log; chmod +777 ${directory}/${rep}/run_${numa}_${rep}.log; done'
