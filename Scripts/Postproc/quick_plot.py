import matplotlib as mpl
mpl.use('Agg')

from matplotlib.ticker import ScalarFormatter
import matplotlib
import matplotlib.gridspec as gspec
import matplotlib.pyplot as plt
import numpy as np
import sys

candsname=sys.argv[1]
snrcut=float(sys.argv[2])
candsfile = np.fromfile(candsname, sep=" ")
candsarr = np.resize(candsfile, (int(np.size(candsfile) / 9), 9))

snrs = candsarr[:, 0]
dms = candsarr[:, 5]
times = candsarr[:,2]
widths = candsarr[:, 3]
members = candsarr[:, 6]


fig = plt.figure(figsize=(20,15))
matplotlib.rcParams.update({'font.size': 12, })

grd = gspec.GridSpec(2,2, height_ratios=[2,1])
grd.update(wspace=0.1, hspace=0.0)
ax1 = plt.subplot(grd[0, :])

frbfig = ax1.scatter(times[snrs > snrcut], dms[snrs > snrcut] + 1, 100, snrs[snrs > snrcut])
cbar = fig.colorbar(frbfig, orientation='horizontal', aspect=60, pad=0.075)
ax1.set(xlabel='Time [s]', ylabel='DM + 1 [pc cm$^{-3}$]')
ax1.set_yscale('log')
ax1.set_ylim(1, 100)
ax1.yaxis.set_major_formatter(ScalarFormatter())
ax1.yaxis.grid(which='both')

ax2 = plt.subplot(grd[1,:-1])
#ax2.hist(candsarr[:, 5] + 1, bins=25, histtype='step', linewidth=2);
ax2.scatter(dms[snrs > snrcut] + 1, members[snrs > snrcut], 100, snrs[snrs > snrcut])
ax2.set(ylabel='Number of counts', xlabel='DM + 1 [pc cm$^{-3}$]')
ax2.set_yscale('log')
ax2.yaxis.set_major_formatter(ScalarFormatter())
ax2.yaxis.grid(which='both')

ax3 = plt.subplot(grd[1:, -1])
widthfig = ax3.scatter(dms[snrs > snrcut] + 1, widths[snrs > snrcut], 100, snrs[snrs > snrcut])
ax3.set(ylabel='Width', xlabel='DM + 1 [pc cm$^{-3}$]')

fig.savefig('time_dm.png')
