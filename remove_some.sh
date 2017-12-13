#!/bin/bash

for node in {0..1} {3..7}
do

    echo "Starting job on node ${node}..."
    ssh pacifix${node} "cd /media/beegfs/; rm -rf 12_12_2017-22:15-121102/"
    
    #nvidia-docker pull docker.mpifr-bonn.mpg.de:5000/paf-test-old:latest; \
    #nvidia-docker tag docker.mpifr-bonn.mpg.de:5000/paf-test-old:latest paf-test-old:latest; \
    #nvidia-docker run --rm -d --net=host -v /media/beegfs/:/beegfs/ paf-test-old /bin/bash -c 'rm -rf /beegfs/11_12_2017-03:45/'"
 
done
