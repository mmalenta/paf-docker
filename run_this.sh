#!/bin/bash



node=$( hostname | sed 's/pacifix\([0-9]*\)/\1/' )

# This is where the output data will go. OBSID is set by the calling script
outdir=/beegfs/PAFJAN/output/${OBSID}

# we also get TOBS
configfile=$outdir/config.${node}.conf

cachedir=/dev/shm
#cachedir=/beegfs/PAFJAN/cache.${node}
#mkdir -p $cachedir

mkdir -p $outdir
nice /home/pulsar/mkeith/redigitise_data.sh $cachedir $outdir 33 > $outdir/pacifix${node}_redig.log 2>&1 &

if [[ -e $configfile ]] ; then
   rm $configfile
fi

touch $configfile; \
echo "IPS 10.17.${node}.1,10.17.${node}.2" >> $configfile; \
echo 'GPUIDS 0,1' >> $configfile; \
echo 'NOBEAMS 1' >> $configfile; \
echo 'NOGPUS 1' >> $configfile; \
echo 'NACCUMULATE 256' >> $configfile; \
echo 'NOSTREAMS 1' >> $configfile; \
echo 'OUTBITS 32' >> $configfile; \
nvidia-docker pull docker.mpifr-bonn.mpg.de:5000/paf-test:latest; \
nvidia-docker tag docker.mpifr-bonn.mpg.de:5000/paf-test:latest paf-test:latest; \


for half in $HALVES ; do
   nvidia-docker run -u 50000:50000 -d --rm --net=host --name paf-pipeline-${half} -v $cachedir:/output/ -v ${outdir}:/beegfs/ --ulimit memlock=-1 paf-test /usr/bin/env node=$node half=$half TOBS=$TOBS /bin/bash -c 'numactl --membind $half --cpunodebind $half /pafinder/bin/pafinder --config /beegfs/config.${node}.conf -o /output/ -r $TOBS -v --numa $half &> /beegfs/pafinder_${node}_${half}.log'
done


echo "STARTED on $node [$HALVES] at "$(date)
