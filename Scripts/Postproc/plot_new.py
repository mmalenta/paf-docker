import matplotlib
matplotlib.use('Agg')

import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import subprocess
import glob
import pandas as pd

canddir = sys.argv[1]
datadir = sys.argv[2]
threadno = int(sys.argv[3])
nothreads = int(sys.argv[4])

headinfo = ['SNR', 'TimeSamp', 'Time', 'Width', 'DmIdx', 'DM', 'Members', 'Begin', 'End',
           'NBeams', 'Mask', 'PrimBeam', 'MaxSNR', 'Beam']
canddata = pd.read_csv(glob.glob(os.path.join(canddir, 'combined/') + '*all.cand')[0], sep='\t', names=headinfo, header=None)
canddata = canddata[(canddata['Mask'] < 65536) & (canddata['SNR'] >= 10.0) & (canddata['DM'] >= 25.0)]
canddata.reset_index(inplace=True, drop=True)

pointpd = pd.read_csv(glob.glob(canddir + '/' + '*pointings.dat')[0], sep='\t', header=None, names=['filename'])
pointpd['mjd'] = pointpd['filename'].str.split('_', expand=True)[1]
pointpd['beam'] = pointpd['filename'].str.split('_', expand=True)[3]
pointpd['mjd'] = pd.to_numeric(pointpd['mjd'])
pointpd['beam'] = pd.to_numeric(pointpd['beam'])
pointpd.sort_values(by='mjd', inplace=True)

startmjd = pointpd['mjd'][0]
canddata = canddata.iloc[0:100]
canddata['mjd'] = startmjd + canddata['Time'] / 86400.0
canddata['filename'] = ""

# NOTE: All the frequencies are expressed in MHz
ftop = 1492.203704
# Single channel band
fchan = 0.592593
nchans = 512
fbottom = ftop - nchans * fchan
# Sampling time in ms
samptime = 54e-03

# NOTE: That doesn't change between candidates - gives dispersion delay in ms
dispconst = 4.15e+06 * (1.0 / (fbottom * fbottom) - 1.0 / (ftop * ftop))

for row in np.arange(canddata.shape[0]):
    canddata.loc[row, 'filename'] = pointpd[(pointpd['beam'] == canddata.iloc[row].Beam) & (pointpd['mjd'] <= canddata.iloc[row].mjd)].sort_values(by='mjd', ascending=False).iloc[0].filename

    fildata = np.fromfile(os.path.join(datadir, canddata.loc[row, 'filename']), dtype=np.uint8)[342:]
    filfile = np.reshape(fildata, (-1, 512)).T
    # TODO: Read just the required portion of the file
    dm = canddata.loc[row, 'DM']    
    dispdelay = dispconst * dm 
    # NOTE: Dispersion delay expressed in the number of time samples
    sampdelay = int(np.ceil(dispdelay / samptime))
    candwidth = 2 ** canddata.loc[row, 'Width']
    # NOTE: We want to have 4 samples over the candidate's width at most
    avgfactor = int(np.ceil(candwidth / 4))
    # NOTE: Padding of 5ms on each side
    padding = int(np.ceil(5 / samptime))
    sampstart = int(canddata.loc[row, 'TimeSamp'] - padding)
    sampuse = int(np.ceil((padding * 2.0 + sampdelay) / avgfactor) * avgfactor)
    outavg = int(sampuse / avgfactor)
       
    # NOTE: Check if we don't have the weird behaviour of candidate detected beyond the accessible time limits
    if (sampstart + 2 * sampuse) < filfile.shape[1]:
        averaged = np.zeros((512, outavg))
        # NOTE: Time average
        for tavg in np.arange(outavg):
            subfil = filfile[:, (sampstart + tavg * avgfactor) : (sampstart + (tavg + 1) * avgfactor)]
            subavg = np.reshape(np.sum(subfil, axis=1), (512, 1))
            averaged[:, tavg] = subavg[:, 0]            
                
        plt.imshow(averaged, aspect='auto', interpolation='none', cmap='binary')
        filenameavg = 'candidate_' + str(canddata.loc[row, 'SNR']) + '_' + str(canddata.loc[row, 'Time']) + '_' + str(dm) + '_avg.png'
        plt.savefig(os.path.join(canddir, 'Plots', filenameavg))
        plt.close()

        # NOTE: Dedisperse to subbands
        # 16 channels ber output band
        # We are looking for signals with SNR of 7.5 and above
        # Will have at least SNR of 7.5 / sqrt(32) = 1.33 per band > 1 as required
        outbands = 16
        perband = int(nchans / outbands)

        subfil = filfile[:, sampstart : sampstart + sampuse + sampuse]

        dedispersed = np.zeros((outbands, sampuse))

        for band in np.arange(outbands):
            subsubfil = subfil[band * perband : (band + 1) * perband, :]
            bandtop = ftop - band * perband * fchan

            for chan in np.arange(perband):
                chanfreq = bandtop - chan * fchan
                delay = int(np.round(4.15e+06 * dm * (1.0 / (chanfreq * chanfreq) - 1.0 / (bandtop * bandtop)) / samptime))
                dedispersed[band, :] = np.add(dedispersed[band, :], subsubfil[chan, delay : delay + sampuse])

            
        plt.imshow(dedispersed, aspect='auto', interpolation='none', cmap='binary')
        filenamededisp = 'candidate_' + str(canddata.loc[row, 'SNR']) + '_' + str(canddata.loc[row, 'Time']) + '_' + str(dm) + '_dedisp.png'
        plt.savefig(os.path.join(canddir, 'Plots', filenamededisp))
        plt.close()

        # NOTE: Time average the dedispersed data
        avgfactor = 32
        dedispavguse = int(np.floor(sampuse / avgfactor) * avgfactor)
        dedispoutavg = int(dedispavguse / avgfactor)

        dedispavg = np.zeros((outbands, dedispoutavg))

        for tavg in np.arange(dedispoutavg):
            subfil = dedispersed[:, tavg * avgfactor : (tavg + 1) * avgfactor]
            subavg = np.reshape(np.sum(subfil, axis = 1), (outbands, 1)) / avgfactor
            dedispavg[:, tavg] = subavg[:, 0]
    
    
        plt.imshow(dedispavg, aspect='auto', interpolation='none', cmap='binary')
        filenamededispavg = 'candidate_' + str(canddata.loc[row, 'SNR']) + '_' + str(canddata.loc[row, 'Time']) + '_' + str(dm) + '_dedisp_avg.png'
        plt.savefig(os.path.join(canddir, 'Plots', filenamededispavg))
        plt.close()

            # NOTE: Full dedispersion
        outbands = 1
        perband = int(nchans / outbands)

        subfil = filfile[:, sampstart : sampstart + sampuse + sampuse]

        dedispersed = np.zeros((outbands, sampuse))

        for band in np.arange(outbands):
            subsubfil = subfil[band * perband : (band + 1) * perband, :]
            bandtop = ftop - band * perband * fchan

            for chan in np.arange(perband):
                chanfreq = bandtop - chan * fchan
                delay = int(np.round(4.15e+06 * dm * (1.0 / (chanfreq * chanfreq) - 1.0 / (bandtop * bandtop)) / samptime))
                dedispersed[band, :] = np.add(dedispersed[band, :], subsubfil[chan, delay : delay + sampuse])


        plt.plot(dedispersed[0, :])
        filename = 'candidate_' + str(canddata.loc[row, 'SNR']) + '_' + str(canddata.loc[row, 'Time']) + '_' + str(dm) + '.png'
        plt.savefig(os.path.join(canddir, 'Plots', filename))
        plt.close()

        print("Processed %.2f%% candidates..." % (row / canddata.shape[0] * 100.0), flush=True, end='\r')
    
print('\n')

        








