#!/bin/bash

for node in {0..1} {3..7}
do

    echo "Starting job on node ${node}..."
    ssh pacifix${node} "cd /media/beegfs/;\
    rm config.conf; \
    touch config.conf; \
    echo 'IPS 10.17.${node}.1,10.17.${node}.2' >> config.conf; \
    echo 'GPUIDS 0,1' >> config.conf; \
    echo 'NOBEAMS 2' >> config.conf; \
    echo 'NOGPUS 2' >> config.conf; \
    nvidia-docker pull docker.mpifr-bonn.mpg.de:5000/paf-test-old:latest; \
    nvidia-docker tag docker.mpifr-bonn.mpg.de:5000/paf-test-old:latest paf-test-old:latest; \
    nvidia-docker run --rm -d --net=host -v /media/beegfs/:/beegfs/ --ulimit memlock=8589934592 paf-test-old /bin/bash -c 'mkdir /beegfs/11_12_2017/0329 -p; /pafinder/bin/pafinder --config /beegfs/config.conf -o /beegfs/11_12_2017/0329 -r 120 -v &> /beegfs/run.log; chmod +777 /beegfs/run.log'"
 
done
