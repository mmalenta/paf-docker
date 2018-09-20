import matplotlib
matplotlib.use('Agg')

import scipy.constants as const
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from astropy.time import Time
from astropy.time import TimeDelta
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
import astropy.coordinates as coord
from astropy import units as u
import os

obsdir = sys.argv[1] #'/beegfs/PAFJAN/heimdall/3C286'

skytime = Time([['2018-01-20T04:09:27', '2018-01-20T04:10:31']], format='isot', scale='utc')
midsky = skytime[0,0] + TimeDelta(30, format='sec')

logtimes = Time([['2018-01-20T04:10:58', '2018-01-20T04:12:03'], ['2018-01-20T04:12:10', '2018-01-20T04:13:15'],
                 ['2018-01-20T04:13:25', '2018-01-20T04:14:29'], ['2018-01-20T04:14:37', '2018-01-20T04:15:42'],
                 ['2018-01-20T04:15:50', '2018-01-20T04:16:54'], ['2018-01-20T04:17:04', '2018-01-20T04:18:08'],
                 ['2018-01-20T04:18:18', '2018-01-20T04:19:23'], ['2018-01-20T04:19:31', '2018-01-20T04:20:35'],
                 ['2018-01-20T04:20:44', '2018-01-20T04:21:48'], ['2018-01-20T04:21:58', '2018-01-20T04:23:03'],
                 ['2018-01-20T04:23:13', '2018-01-20T04:24:17'], ['2018-01-20T04:24:26', '2018-01-20T04:25:30'],
                 ['2018-01-20T04:25:40', '2018-01-20T04:26:44'], ['2018-01-20T04:26:53', '2018-01-20T04:27:57'],
                 ['2018-01-20T04:28:06', '2018-01-20T04:29:10'], ['2018-01-20T04:29:20', '2018-01-20T04:30:25'],
                 ['2018-01-20T04:30:35', '2018-01-20T04:31:39'], ['2018-01-20T04:31:48', '2018-01-20T04:32:52'],
                 ['2018-01-20T04:33:03', '2018-01-20T04:34:07'], ['2018-01-20T04:34:16', '2018-01-20T04:35:21'],
                 ['2018-01-20T04:35:37', '2018-01-20T04:36:42'], ['2018-01-20T04:36:54', '2018-01-20T04:37:58']],
                format='isot', scale='utc')
midtimes = logtimes[:, 0] + TimeDelta(30, format='sec')

tsamp = 54e-06

usesec = 30.0
usesamp = int(np.floor(usesec / tsamp))

skyfil = np.reshape(np.fromfile(os.path.join(obsdir, 'I_58138.17135348_beam_0_8bit.fil'), dtype=np.uint8)[342: ], (-1, 512)).T
skyscaling = np.genfromtxt(os.path.join(obsdir, 'I_58138.17135348_beam_0_8bit.fil.scale'))
skyoffset = np.reshape(skyscaling[:, 1], (512, 1))
skyscale = np.reshape(skyscaling[:, 2], (512, 1))

skyskip = int(np.ceil((midsky.mjd - 58138.17135348) * 86400 / tsamp))
skyfil = (skyfil[:, skyskip : skyskip + usesamp] - 64.5) / skyscale + skyoffset
skyband = np.sum(skyfil, axis=1) / usesamp

skyfils = ['I_58138.17135348_beam_0_8bit.fil',
            'I_58138.17135313_beam_1_8bit.fil',
            'I_58138.17129031_beam_2_8bit.fil',
            'I_58138.17129953_beam_3_8bit.fil',
            'I_58138.17134246_beam_4_8bit.fil',
            'I_58138.17135614_beam_5_8bit.fil',
            'I_58138.17128600_beam_6_8bit.fil',
            'I_58138.17134417_beam_7_8bit.fil',
            'I_58138.17132950_beam_8_8bit.fil',
            'I_58138.17135699_beam_9_8bit.fil',
            'I_58138.17127571_beam_10_8bit.fil',
            'I_58138.17135221_beam_11_8bit.fil',
            'I_58138.17127636_beam_12_8bit.fil',
            'I_58138.17136662_beam_13_8bit.fil',
            'I_58138.17131382_beam_14_8bit.fil',
            'I_58138.17137507_beam_15_8bit.fil',
            'I_58138.17128362_beam_16_8bit.fil']

skymjds = [filfile.split('_')[1] for filfile in skyfils]
skyscales = [filfile + '.scale' for filfile in skyfils]

beamfils = ['I_58138.17405684_beam_0_8bit.fil',
            'I_58138.17405649_beam_1_8bit.fil',
            # Must be merged with I_58138.17669703_beam_2_8bit.fil
            # I am pretty sure that the single file just about cuts it, with 2s edge
            'I_58138.17399367_beam_2_8bit.fil',
            'I_58138.17670625_beam_3_8bit.fil',
            'I_58138.17674918_beam_4_8bit.fil',
            'I_58138.17676286_beam_5_8bit.fil',
            'I_58138.17939608_beam_6_8bit.fil',
            'I_58138.17945425_beam_7_8bit.fil',
            'I_58138.17943958_beam_8_8bit.fil',
            'I_58138.18217043_beam_9_8bit.fil',
            'I_58138.18208915_beam_10_8bit.fil',
            'I_58138.18216565_beam_11_8bit.fil',
            'I_58138.18479316_beam_12_8bit.fil',
            'I_58138.18488342_beam_13_8bit.fil',
            'I_58138.18483062_beam_14_8bit.fil',
             # Must be merged with I_58138.18759523_beam_15_8bit.fil
             # This definitely has to be merged - we get less than half of the data
            'I_58138.18489187_beam_15_8bit.fil',
            'I_58138.18750378_beam_16_8bit.fil']

filmjds = [filfile.split('_')[1] for filfile in beamfils]
beamscales = [filfile + '.scale' for filfile in beamfils]
 
#skydata = np.fromfile(os.path.join(obsdir, 'I_58138.17135348_beam_0_8bit.fil'), dtype=np.uint8)[342:]
#skyscaling = np.genfromtxt(os.path.join(obsdir, 'I_58138.17135348_beam_0_8bit.fil.scale'))
#skyfildata = np.reshape(skydata, (-1, 512)).T
#skyoffset = np.reshape(skyscaling[:, 1], (512, 1))
#skyscale = np.reshape(skyscaling[:, 2], (512, 1))
#skyskip = int(np.ceil((midsky.mjd - 58138.17135348) * 86400.0 / tsamp))
#skyfildata = (skyfildata[:, skyskip : (skyskip + usesamp)] - 64.5) / skyscale + skyoffset

#skyband = np.sum(skyfildata, axis=1) / usesamp

colours = ['black', 'gray', 'red', 'sienna', 'sandybrown', 'tan', 'gold', 'olivedrab', 'chartreuse',
         'darkgreen', 'deepskyblue', 'blue', 'darkorchid', 'm', 'navy', 'silver', 'darkorange']

topfreq = 1492.203704
band = 0.592593
nchans = 512
frequencies = topfreq - np.arange(512) * band

# MODELLING THE 3C286 SFD
a0 = 1.2418
a1 = -0.4507
a2 = -0.1798
a3 = 0.0357
gfrequencies = frequencies / 1000.0
logsfd = a0 + a1 * np.log10(gfrequencies) + a2 * (np.log10(gfrequencies)) ** 2.0 + a3 * (np.log10(gfrequencies)) ** 3.0
sfd = 10 ** logsfd

area = const.pi * 50 ** 2

figpower = plt.figure(figsize=(15,10))
axpower = figpower.gca()

figtsys = plt.figure(figsize=(15,10))
axtsys = figtsys.gca()

figsky = plt.figure(figsize=(15,10))
axsky = figsky.gca()

allbands = np.zeros((17, 512))
alltsys = np.zeros((17, 512))
allsky = np.zeros((17, 512))

for ibeam in np.arange(17):
    print("Processing beam %i" % ibeam)
    skyfil = np.reshape(np.fromfile(os.path.join(obsdir, skyfils[ibeam]), dtype=np.uint8)[342: ], (-1, 512)).T
    skyscaling = np.genfromtxt(os.path.join(obsdir, skyscales[ibeam]))
    skyoffset = np.reshape(skyscaling[:, 1], (512, 1))
    skyscale = np.reshape(skyscaling[:, 2], (512, 1))

    skyskip = int(np.ceil((midsky.mjd - np.float(skymjds[ibeam])) * 86400 / tsamp))
    skyfil = (skyfil[:, skyskip : skyskip + usesamp] - 64.5) / skyscale + skyoffset
    skyband = np.sum(skyfil, axis=1) / usesamp

    allsky[ibeam, :] = skyband

    beamfil = np.reshape(np.fromfile(os.path.join(obsdir, beamfils[ibeam]), dtype=np.uint8)[342:], (-1, 512)).T
    beamscaling = np.genfromtxt(os.path.join(obsdir, beamscales[ibeam]))
    beamoffset = np.reshape(beamscaling[:, 1], (512, 1))
    beamscale = np.reshape(beamscaling[:, 2], (512, 1))

    beamskip = int(np.ceil((midtimes[ibeam].mjd - np.float(filmjds[ibeam])) * 86400 / tsamp))
    beamfil = (beamfil[:, beamskip : beamskip + usesamp] - 64.5) / beamscale + beamoffset

    if beamfil.shape[1] != usesamp:
        print("Something went wrong for file %s\n" % beamfils[ibeam])
        beamband = np.sum(beamfil, axis=1) / beamfil.shape[1]
    else:
        beamband = np.sum(beamfil, axis=1) / usesamp 

    allbands[ibeam, :] = beamband

    yfactor = beamband / skyband
    yfactor[yfactor == 1] = 1.01

    tsys = area * (sfd * 1e-26) / (2.0 * const.k * (yfactor - 1.0))

    alltsys[ibeam, :] = tsys

    axpower.plot(frequencies, beamband, color=colours[ibeam], linewidth=1, label='Beam ' + str(ibeam))
    axtsys.plot(frequencies, tsys, color=colours[ibeam], linewidth=1, label='Beam ' + str(ibeam))
    axsky.plot(frequencies, skyband, color=colours[ibeam], linewidth=1, label='Sky beam ' + str(ibeam))

axpower.set_title('3C286 power')
axtsys.set_title('Tsys / eta')
axsky.set_title('Sky reference power')

axtsys.set_ylim([50, 150])

axpower.legend()
axtsys.legend()
axsky.legend()

figpower.savefig(os.path.join(obsdir, 'beams_power.png'))
figtsys.savefig(os.path.join(obsdir, 'beams_tsys.png'))
figsky.savefig(os.path.join(obsdir, 'beams_sky.png'))

np.savetxt(os.path.join(obsdir, 'beams_power.txt'), allbands)
np.savetxt(os.path.join(obsdir, 'beams_tsys.txt'), alltsys)
