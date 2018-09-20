import matplotlib.pyplot as plt
import numpy as np
import os
import sys

canddir = sys.argv[1]
datadir = sys.argv[2]
beam = sys.argv[2]
snrlow = 5.0
snrhigh = 100.0

filfiles = []
mjds = []

for filfile in sorted(os.listdir(datadir)):
    if(filfile.endswith('_0_8bit.fil')):
        filfiles.append(filfile)

filfiles = np.array(filfiles)

for filfile in filfiles:
    mjds.append(filfile.split('_')[1])

mjds = np.array(mjds)
mjds = np.reshape(mjds, (-1, 1))
filfiles = np.reshape(filfiles, (-1, 1))

combined = np.append(filfiles, mjds, axis=1)

for candfile in sorted(os.listdir(canddir)):
    if (candfile.endswith(beam + '.cand')):
        if os.stat(os.path.join(canddir, candfile)).st_size > 0:
            print("Processing file %s" % candfile) 
            
            data = np.genfromtxt(os.join(datadir, candfile), delimiter='\t', names=['SNR', 'TimeSamp', 'Time', 'Width', 'DmIdx', 'DmValue', 'Members', 'Begin', 'End'])
            filtered = data[np.where((data['SNR'] > snrlow) & (data['SNR'] <= snrhigh))]
            
            for candidate in filtered:
                subprocess.call("dedisperse", infile, "-d", dm, "-headerless", "-nobaseline"

