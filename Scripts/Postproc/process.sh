#!/bin/bash

beamno=$1
gpu=$2
outdir=/output/NEW_PROC/2018-01-23_031226
datadir=/data/2018-01-23_031226

mkdir ${outdir} -p
cd ${outdir}

for obsfile in $( ls -1 ${datadir}/*beam_${beamno}_8bit.fil )
do
    sourcename=$(basename ${obsfile} | sed "s/\(I_[0-9]*.[0-9]*\)_beam_${beamno}_8bit.fil/\1/")
    echo "Processing file ${sourcename}"

    /heimdall/Applications/heimdall -f ${obsfile} -gpu_id ${gpu} -output_dir ${outdir} -dm 0 2000 -V -detect_thresh 7.5
done
