#!/bin/bash

# this will be the observation ID used in this run
obsid=`date -u +%Y-%m-%d_%H%M%S`
tobs=300
numlaunched=0
if [[ -n "$1" ]] ; then
	tobs=$1
fi

echo "OBSID=$obsid TOBS=$tobs"

outdir=/beegfs/PAFAUG/output/${obsid}
mkdir -p ${outdir}

cp /beegfs/PAFAUG/tests/header.dada ${outdir}

rm pafinder.launch.*.log
# Nodes 0,1,3-8 have two beams. Node 2 currently has a bad NIC and can only take 1 beam.
#for node in {0..1} {3..8} 
#for node in {0..1} {3..7} 
#for node in 2
for node in {0..8}
do
    echo "Starting job on node ${node}..."
    ssh pacifix${node} "/usr/bin/env OBSID=$obsid TOBS=$tobs HALVES='0 1' bash -s" < run_this.sh > ${outdir}/launch.${node}.log &
    numlaunched=$((numlaunched+2))
done

# Make node 2 a special case MJK 2018-01-19
node=2
#echo "Starting job on node ${node}..."
#ssh pacifix${node} "/usr/bin/env OBSID=$obsid TOBS=$tobs HALVES='1' bash -s" < run_this.sh > ${outdir}/pafinder.launch.${node}.log &
#numlaunched=$((numlaunched+1))

echo "Launched ${numlaunched} beam processing"
# NOTE: This has to be removed if the pipeline is not using the new startup procedure
python /home/pulsar/soft/paf-docker/Scripts/FullPipeline/get_start_time.py ${numlaunched} ${outdir} 

wait

