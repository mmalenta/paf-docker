#!/bin/bash

for node in {0..1} {3..8} 
do
    echo "Starting job on node ${node}..."
    ssh pacifix${node} 'bash -s' < run_this.sh
done


        #nvidia-docker run --rm -d --net=host -v /media/beegfs/:/beegfs/ --ulimit memlock=8589934592 paf-new /bin/bash -c 'for rep in $(seq 1 ${reps}); do mkdir ${directory}/${rep} -p; touch ${directory}/${rep}/run_${numa}_${rep}; done'"
        #numactl --membind ${numa} --cpunodebind ${numa} /pafinder/bin/pafinder --config /beegfs/config.conf -o ${directory}/${rep} -r 300 -v --numa ${numa} &> ${directory}/${rep}/run_${numa}_${rep}.log; chmod +777 ${directory}/${rep}/run_${numa}_${rep}.log; done'
