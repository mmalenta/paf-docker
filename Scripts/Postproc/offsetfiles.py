import pandas as pd
import numpy as np
import os
import sys
import astropy as ap
from astropy.time import Time

obsdir = sys.argv[1]
pointings = np.genfromtxt(obsdir + '/' + obsdir + '_pointings.dat', dtype='str')
pointpd = pd.DataFrame(pointings, columns=['filename'])

pointpd['mjd'] = pointpd['filename'].str.split('_', expand=True)[1]
pointpd['beam'] = pointpd['filename'].str.split('_', expand=True)[3]
pointpd['mjd'] = pd.to_numeric(pointpd['mjd'])
pointpd['beam'] = pd.to_numeric(pointpd['beam'])
pointpd.sort_values(by='mjd', inplace=True)

samptime = 54e-06;
first_time = pointpd['mjd'][0]
pointpd['offset'] = (pointpd['mjd'] - first_time) * 86400.0
pointpd['sampoffset'] = pd.to_numeric(np.ceil(pointpd['offset'] / samptime), downcast='integer')

datadir = obsdir

candfiles = []

for candfile in sorted(os.listdir(datadir)):
    if (candfile.endswith('cand')):
        candfiles.append(candfile)
        
candpd = pd.DataFrame(candfiles, columns=['filename'])
candpd['date'] = candpd['filename'].str.split('.', expand=True)[0].str.split('_', expand=True)[0]
candpd['beam'] = candpd['filename'].str.split('.', expand=True)[0].str.split('_', expand=True)[1]
#candpd['date'] = candpd['date'].str.replace('22-', '22T')
candpd['date'] = candpd['date'].str.replace('-', 'T')
candpd['date'] = candpd['date'].str.replace('2018T01T', '2018-01-')

dates = candpd['date'].values.tolist()
candpd['mjd'] = Time(dates, format='isot', scale='utc').mjd
candpd['startmjd'] = 0
candpd['offset'] = 0

# I am very proud of this code below
candpd.loc[candpd.beam == '00', 'beam'] = '0'
candpd.loc[candpd.beam == '01', 'beam'] = '1'
candpd.loc[candpd.beam == '02', 'beam'] = '2'
candpd.loc[candpd.beam == '03', 'beam'] = '3'
candpd.loc[candpd.beam == '04', 'beam'] = '4'
candpd.loc[candpd.beam == '05', 'beam'] = '5'
candpd.loc[candpd.beam == '06', 'beam'] = '6'
candpd.loc[candpd.beam == '07', 'beam'] = '7'
candpd.loc[candpd.beam == '08', 'beam'] = '8'
candpd.loc[candpd.beam == '09', 'beam'] = '9'
candpd['beam'] = pd.to_numeric(candpd['beam'])

ifile = 0;
numfiles = len(candpd);

print(numfiles)

beams = ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18']

outdir = os.path.join(obsdir, 'combined')

if not os.path.exists(outdir):
    os.makedirs(outdir)

for ibeam in candpd.beam.unique():

    curbeam = beams[int(ibeam)];
    repbeam = beams[int(ibeam) + 1];
    
    mymjd = candpd[candpd.beam == ibeam].mjd.values

    for imjd in mymjd:
        pointmjd = sorted(pointpd[(pointpd.beam == ibeam) & (pointpd.mjd <= imjd)].mjd.values, reverse=True)[0]
        offset = pointpd[(pointpd.mjd == pointmjd) & (pointpd.beam == ibeam)].offset.values
        sampoffset = pointpd[(pointpd.mjd == pointmjd) & (pointpd.beam == ibeam)].sampoffset.values
        candpd.loc[(candpd.beam == ibeam) & (candpd.mjd == imjd), 'startmjd'] = pointmjd
        candpd.loc[(candpd.beam == ibeam) & (candpd.mjd == imjd), 'offset'] = offset
        candpd.loc[(candpd.beam == ibeam) & (candpd.mjd == imjd), 'sampoffset'] = sampoffset

    firstfile=sorted(candpd[candpd.beam == ibeam].filename.values)[0]
    firstfile = firstfile.replace(curbeam + '.cand', repbeam + '.cand')
    with open(os.path.join(outdir, firstfile), 'a') as ff:    
        for filename in candpd[candpd.beam == ibeam].filename.values:
            ifile += 1;
            if os.stat(os.path.join(obsdir, filename)).st_size > 0:
                print("Processing file %s (%.2f%%)" % (filename, (ifile / numfiles * 100.0)), flush=True, end='\r')
                #print("Processing file %s (%.2f%%)" % (filename, (ifile / numfiles * 100.0)), end='\r')
                filevals = pd.read_csv(os.path.join(obsdir, filename), sep='\t', header=None)
        
                filevals.iloc[:, 2] = filevals.iloc[:, 2] + candpd[candpd.filename == filename].offset.values
                filevals.iloc[:, 1] = filevals.iloc[:, 1] + int(candpd[candpd.filename == filename].sampoffset.values) 
                filevals.iloc[:, 7] = filevals.iloc[:, 7] + int(candpd[candpd.filename == filename].sampoffset.values)
                filevals.iloc[:, 8] = filevals.iloc[:, 8] + int(candpd[candpd.filename == filename].sampoffset.values)
 
                filevals.to_csv(path_or_buf=ff, sep='\t', index=False, header=False, float_format='%.5f')

print('\n')

