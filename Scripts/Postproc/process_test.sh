#!/bin/bash

outdir=/output/Scaling/OldScale
datadir=/data/

mkdir ${outdir} -p
cd ${outdir}

for obsfile in $( ls -1 ${datadir}/*beam_0_8bit.fil )
do
    sourcename=$(basename ${obsfile} | sed "s/\(I_[0-9]*.[0-9]*\)_beam_0_8bit.fil/\1/")
    echo "Processing file ${sourcename}"

    /heimdall/Applications/heimdall -f ${obsfile} -gpu_id ${gpu} -output_dir ${outdir} -dm 0 2000 -V -detect_thresh 7.5
done
