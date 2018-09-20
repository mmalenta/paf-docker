import matplotlib
matplotlib.use('Agg')

import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import glob
import pandas as pd
from astropy.time import Time

canddir = sys.argv[1]
datadir = sys.argv[2]
beamno = sys.argv[3]

# NOTE: .cand files use 00, 01, 02, 03, ... to label beams, when .fil files use 0, 1, 2, etc
# Need to remove the trailing 0 if necessary
if beamno[0] == '0':
    filbeam = beamno[1]
else:
    filbeam = beamno

headinfo = ['SNR', 'TimeSamp', 'Time', 'Width', 'DmIdx', 'DM', 'Members', 'Begin', 'End']

candfiles = sorted(glob.glob(canddir + '/*' + beamno + '.cand'))

#print(candfiles)

pointpd = pd.read_csv(glob.glob(canddir + '/' + '*pointings.dat')[0], sep='\t', header=None, names=['filename'])
pointpd['mjd'] = pointpd['filename'].str.split('_', expand=True)[1]
pointpd['beam'] = pointpd['filename'].str.split('_', expand=True)[3]
pointpd['mjd'] = pd.to_numeric(pointpd['mjd'])
pointpd['beam'] = pd.to_numeric(pointpd['beam'])

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

for fullcandfile in candfiles:
  
    if os.stat(fullcandfile).st_size > 0:
        canddata = pd.read_csv(fullcandfile, sep='\t', header=None, usecols=np.arange(9), names = headinfo)
        #print(canddata)
        candfile = os.path.basename(fullcandfile)
        print("Processing file %s" % candfile)
        candfiledate = candfile.split('_')[0]
        candfiledate = candfiledate.replace('-', 'T')
        candfiledate = candfiledate.replace('2018T01T', '2018-01-')
    
        candfilemjd = Time(candfiledate, format='isot', scale='utc').mjd 

        filname = pointpd[(pointpd.beam == int(filbeam)) & (pointpd.mjd <= candfilemjd)].sort_values(by='mjd', ascending=False).iloc[0].filename
        print("Filterbank file used %s" % filname)
        fildata = np.fromfile(os.path.join(datadir, filname), dtype=np.uint8)[342:]
        filfile = np.reshape(fildata, (-1, 512)).T

        for row in np.arange(canddata.shape[0]):
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
                filenameavg = 'candidate_' + str(canddata.loc[row, 'SNR']) + '_' + str(canddata.loc[row, 'Time']) + '_' + str(dm) + '_' + beamno + '_avg.png'
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
                filenamededisp = 'candidate_' + str(canddata.loc[row, 'SNR']) + '_' + str(canddata.loc[row, 'Time']) + '_' + str(dm) + '_' + beamno + '_dedisp.png'
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
                filenamededispavg = 'candidate_' + str(canddata.loc[row, 'SNR']) + '_' + str(canddata.loc[row, 'Time']) + '_' + str(dm) + '_' + beamno + '_dedisp_avg.png'
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
                filename = 'candidate_' + str(canddata.loc[row, 'SNR']) + '_' + str(canddata.loc[row, 'Time']) + '_' + str(dm) + '_' + beamno + '.png'
                plt.savefig(os.path.join(canddir, 'Plots', filename))
                plt.close()

    
print('\n')

        








