import matplotlib
matplotlib.use('Agg')

import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import subprocess

canddir = sys.argv[1]
datadir = sys.argv[2]
threadno = int(sys.argv[3])
nothreads = int(sys.argv[4])

data = np.genfromtxt(os.path.join(canddir, 'for_dedisp.dat'), delimiter='\t', dtype=str)
datalen = len(data)
perthread = int(np.ceil(float(datalen) / nothreads))
print(perthread)

data = data[((threadno - 1) * perthread) : (threadno * perthread)]
print(data)

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

for candfile in data:
    # Files should exist, but better to check
    # Files should all have candidates in, but better to check
    # Load candidates, check which candidates have SNR grater than threshold and lower than threshold
    # Run dedisperse for each candidate

    print('Processing candidate file %s' % candfile[0])

    canddata = np.fromfile(os.path.join(canddir,  candfile[0]), sep='\t')
    canddata = np.reshape(canddata, (-1, 9))
    filtered = canddata[(canddata[:, 0] >= 10.0) & (canddata[:, 5] >= 25.0)]

    for filcand in filtered:

        #ff = open(os.path.join(canddir, 'dedisp' + str(threadno - 1) + '.dat'), 'wb')
        #subprocess.call(['dedisperse', os.path.join(datadir, candfile[1]), "-d", str(filcand[5]), '-headerless', '-nobaseline'], stdout=ff)
        #ff.close()

        #dedisp = np.fromfile(os.path.join(canddir, 'dedisp' + str(threadno - 1) + '.dat'), dtype=np.float32)
        #candsamp = int(filcand[1])
        #plt.plot(dedisp[candsamp - 1024 : candsamp + 1024])
        #filenametimepower = 'candidate_' + str(filcand[0]) + '_' + str(filcand[2]) + '_' + str(filcand[5]) + '.png'
        #plt.savefig(os.path.join(canddir, 'Plots', filenametimepower))
        #plt.close()

        # TODO: Use the Python dedispersion implementation to speed up the slow code above - we won't be dedispersing the whole time series every time

        # NOTE: This assumes that the header has the size of 342B
        fildata = np.fromfile(os.path.join(datadir, candfile[1]), dtype=np.uint8)[342:]
        filfile = np.reshape(fildata, (-1, 512)).T
        # TODO: Read just the required portion of the file
        dispdelay = dispconst * filcand[5]
        # NOTE: Dispersion delay expressed in the number of time samples
        sampdelay = int(np.ceil(dispdelay / samptime))
        candwidth = 2 ** filcand[3]
        # NOTE: We want to have 4 samples over the candidate's width at most
        avgfactor = int(np.ceil(candwidth / 4))
        # NOTE: Padding of 5ms on each side
        padding = int(np.ceil(5 / samptime))
        sampstart = int(filcand[1] - padding)
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
            filenameavg = 'candidate_' + str(filcand[0]) + '_' + str(filcand[2]) + '_' + str(filcand[5]) + '_avg.png'
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
                    delay = int(np.round(4.15e+06 * filcand[5] * (1.0 / (chanfreq * chanfreq) - 1.0 / (bandtop * bandtop)) / samptime))
                    dedispersed[band, :] = np.add(dedispersed[band, :], subsubfil[chan, delay : delay + sampuse])

            
            plt.imshow(dedispersed, aspect='auto', interpolation='none', cmap='binary')
            filenamededisp = 'candidate_' + str(filcand[0]) + '_' + str(filcand[2]) + '_' + str(filcand[5]) + '_dedisp.png'
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
            filenamededispavg = 'candidate_' + str(filcand[0]) + '_' + str(filcand[2]) + '_' + str(filcand[5]) + '_dedisp_avg.png'
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
                    delay = int(np.round(4.15e+06 * filcand[5] * (1.0 / (chanfreq * chanfreq) - 1.0 / (bandtop * bandtop)) / samptime))
                    dedispersed[band, :] = np.add(dedispersed[band, :], subsubfil[chan, delay : delay + sampuse])


            plt.plot(dedispersed[0, :])
            filename = 'candidate_' + str(filcand[0]) + '_' + str(filcand[2]) + '_' + str(filcand[5]) + '.png'
            plt.savefig(os.path.join(canddir, 'Plots', filename))
            plt.close()

        else:
            print('Bad time sample of the event')

        








