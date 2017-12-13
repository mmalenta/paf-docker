#!/bin/bash

node=$( hostname | sed 's/pacifix\([0-9]*\)/\1/' )

cd /media/beegfs; \
rm config.conf; \
touch config.conf; \
echo "IPS 10.17.${node}.1,10.17.${node}.2" >> config.conf; \
echo 'GPUIDS 0,1' >> config.conf; \
echo 'NOBEAMS 1' >> config.conf; \
echo 'NOGPUS 1' >> config.conf; \
echo 'NACCUMULATE 256' >> config.conf; \
echo 'NOSTREAMS 1' >> config.conf; \
echo 'OUTBITS 32' >> config.conf; \
nvidia-docker pull docker.mpifr-bonn.mpg.de:5000/paf-new:latest; \
nvidia-docker tag docker.mpifr-bonn.mpg.de:5000/paf-new:latest paf-new:latest; \

nvidia-docker run --rm -d --net=host -v /media/beegfs/:/beegfs/ --ulimit memlock=8589934592 paf-new /bin/bash -c 'for rep in {1..24}; do mkdir /beegfs/13_12_2017-01:45-121102/${rep} -p; \
chmod +777 /beegfs/13_12_2017-01:45-121102/; chmod +777 /beegfs/13_12_2017-01:45-121102/${rep}; \
numactl --membind 0 --cpunodebind 0 /pafinder/bin/pafinder --config /beegfs/config.conf -o /beegfs/13_12_2017-01:45-121102/${rep} -r 300 -v --numa 0 &> /beegfs/13_12_2017-01:45-121102/${rep}/run_0_${rep}.log; \
chmod +777 /beegfs/13_12_2017-01:45-121102/run_0_${rep}.log; done'

nvidia-docker run --rm -d --net=host -v /media/beegfs/:/beegfs/ --ulimit memlock=8589934592 paf-new /bin/bash -c 'for rep in {1..24}; do mkdir /beegfs/13_12_2017-01:45-121102/${rep} -p; \
chmod +777 /beegfs/13_12_2017-01:45-121102/; chmod +777 /beegfs/13_12_2017-01:45-121102/${rep}; \
numactl --membind 1 --cpunodebind 1 /pafinder/bin/pafinder --config /beegfs/config.conf -o /beegfs/13_12_2017-01:45-121102/${rep} -r 300 -v --numa 1 &> /beegfs/13_12_2017-01:45-121102/${rep}/run_1_${rep}.log; \
chmod +777 /beegfs/13_12_2017-01:45-121102/run_1_${rep}.log; done'

