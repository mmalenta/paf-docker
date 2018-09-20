import matplotlib
matplotlib.use('Agg')

import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import subprocess

canddir = sys.argv[1]
datadir = sys.argv[2]

data = np.genfromtxt(os.path.join(canddir, 'for_dedisp.dat'), delimiter='\t', dtype=str)

for candfile in data:
    # Files should exist, but better to check
    # Files should all have candidates in, but better to check
    # Load candidates, check which candidates have SNR grater than threshold and lower than threshold
    # Run dedisperse for each candidate

    print('Processing candidate file %s' % candfile[0])

    canddata = np.fromfile(os.path.join(canddir,  candfile[0]), sep='\t')
    canddata = np.reshape(canddata, (-1, 9))
    filtered = canddata[canddata[:, 0] >= 7.5]

    for filcand in filtered:

        ff = open(os.path.join(canddir, 'dedisp.dat'), 'wb')
        subprocess.call(['dedisperse', os.path.join(datadir, candfile[1]), "-d", str(filcand[5]), '-headerless', '-nobaseline'], stdout=ff)
        ff.close()

        dedisp = np.fromfile(os.path.join(canddir, 'dedisp.dat'), dtype=np.float32)
        candsamp = int(filcand[1])
        plt.plot(dedisp[candsamp - 1024 : candsamp + 1024])
        filename = 'candidate_' + str(filcand[0]) + '_' + str(filcand[2]) + '_' + str(filcand[5]) + '.png'
        plt.savefig(os.path.join(canddir, 'Plots', filename))
        plt.close()
