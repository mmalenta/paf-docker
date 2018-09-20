#!/bin/bash

node=$( hostname | sed 's/pacifix\([0-9]*\)/\1/' )

# This is where the output data will go. OBSID is set by the calling script
outdir=/beegfs/PAFAUG/output/${OBSID}
canddir=${outdir}/cands
mkdir -p $canddir
# We also get TOBS
configfile=$outdir/config.${node}.conf

#cachedir=/dev/shm
#cachedir=/beegfs/PAFJAN/cache.${node}
#mkdir -p $cachedir

# NOTE: We should not need the externak redigitiser with the new scaling pipeline
#nice /home/pulsar/mkeith/redigitise_data.sh $cachedir $outdir 33 > $outdir/pacifix${node}_redig.log 2>&1 &

if [[ -e $configfile ]] ; then
   rm $configfile
fi

# NOTE: That currently doesn't work with Docker
#nvidia-cuda-mps-control -d

touch $configfile; \
echo "IPS 10.17.${node}.1,10.17.${node}.2" >> $configfile; \
echo 'GPUIDS 0,1' >> $configfile; \
echo 'NOBEAMS 1' >> $configfile; \
echo 'NOGPUS 1' >> $configfile; \
echo 'NACCUMULATE 256' >> $configfile; \
echo 'NOSTREAMS 1' >> $configfile; \
echo 'OUTBITS 8' >> $configfile; \
echo 'DEDISPGULP 262144' >> $configfile; \
nvidia-docker pull docker.mpifr-bonn.mpg.de:5000/paf-test:latest; \
nvidia-docker tag docker.mpifr-bonn.mpg.de:5000/paf-test:latest paf-test:latest; \

nvidia-docker pull docker.mpifr-bonn.mpg.de:5000/paf-heimdall:latest; \
nvidia-docker tag docker.mpifr-bonn.mpg.de:5000/paf-heimdall:latest paf-heimdall:latest; \

export PSRHOME=/home/pulsar/.local
export TEMPO2=${PSRHOME}
export CUDA_ROOT=/usr/local/cuda
export PSRCAT_FILE=/home/pulsar/.local/psrcat/psrcat.db

export PATH=/sbin/:${PSRHOME}/bin:${HOME}/bin:${CUDA_ROOT}/bin:${PATH}:/home/pulsar/.local/bin/fv5.4

if [ -z $LD_LIBRARY_PATH ];
then
    export LD_LIBRARY_PATH=${CUDA_ROOT}/lib64:${PSRHOME}/lib
else
    export LD_LIBRARY_PATH=${CUDA_ROOT}/lib64:${PSRHOME}/lib:${LD_LIBRARY_PATH}
fi

if [ -z $C_INCLUDE_PATH ];
then
    export C_INCLUDE_PATH=${CUDA_ROOT}/include/:${PSRHOME}/include
else
    export C_INCLUDE_PATH=${CUDA_ROOT}/include/:${PSRHOME}/include:${C_INCLUDE_PATH}
fi

if [ -z $PYTHONPATH ];
then
    export PYTHONPATH=/home/pulsar/xinping/pythonlib
else
    export PYTHONPATH=/home/pulsar/xinping/pythonlib:${PYTHONPATH}
fi

keyends=(a c)

for half in $HALVES ; do
#for half in 0 ; do

   nodedir=${node}_${half}
   dadadir=${outdir}/${nodedir}
   mkdir -p ${dadadir}
   dadakey=dada${keyends[${half}]}
   #dada_db -d -k ${dadakey}

   # IF BOTH DADA_DBDISK AND HEIMDALL RUNNING: -r 2
   # IF ONLY DADA_DBDISK RUNNING: -r 1
   #dada_db -b 134217728 -n 16 -k $dadakey -r 2

   #dada_dbdisk -k ${dadakey} -D ${dadadir} -d -t 268435456

   # START HEIMDALL
   nvidia-docker run -u 50000:50000 --privileged -d --rm --net=host --ipc=host --name paf-heimdall-${half} -v ${outdir}:/output --ulimit memlock=-1 paf-heimdall /usr/bin/env half=$half dadakey=$dadakey nodedir=$nodedir /bin/bash -c "dada_db -b 134217728 -n 16 -k $dadakey -r 2; dada_dbdisk -k $dadakey -D /output/$nodedir -d -t 268435456; numactl --membind $half --cpunodebind $half /heimdall-paf/Applications/heimdall -V -k $dadakey -gpu_id $half -nsamps_gulp 262144 -output_dir /output/cands -dm 0 2000 -detect_thresh 7.5 &> /output/heimdall_${node}_${half}.log; dada_db -d -k $dadakey"

   # START PAFINDER
   nvidia-docker run -u 50000:50000 --privileged -d --rm --net=host --ipc=host --name paf-pipeline-${half} -v ${outdir}:/beegfs/ --ulimit memlock=-1 paf-test /usr/bin/env dadakey=$dadakey node=$node half=$half TOBS=$TOBS /bin/bash -c 'numactl --membind $half --cpunodebind $half /pafinder/bin/pafinder --config /beegfs/config.${node}.conf -o /beegfs/ -k $dadakey --dadaheader /beegfs/header.dada -r $TOBS -v --numa $half &> /beegfs/pafinder_${node}_${half}.log'
done


echo "STARTED on $node [$HALVES] at "$(date)
