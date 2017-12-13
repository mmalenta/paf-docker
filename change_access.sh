#!/bin/bash

for node in {0..1} {3..7}
do

    echo "Starting job on node ${node}..."
    ssh pacifix${node} "cd /media/beegfs/;\
    nvidia-docker pull docker.mpifr-bonn.mpg.de:5000/paf-test-old:latest; \
    nvidia-docker tag docker.mpifr-bonn.mpg.de:5000/paf-test-old:latest paf-test-old:latest; \
    nvidia-docker run --rm -d --net=host -v /media/beegfs/:/beegfs/ paf-test-old /bin/bash -c 'chmod +777 /beegfs/11_12_2017/0329'" 
 
done
