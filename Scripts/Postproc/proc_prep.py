import numpy as np
import os
import sys
import astropy as ap
import pandas as pd
from astropy.time import Time

canddir = sys.argv[1]
datadir = sys.argv[2]
beam = sys.argv[3]
snrlow = 5.0
snrhigh = 100.0

filfiles = []
mjds = []

for filfile in sorted(os.listdir(datadir)):
    if(filfile.endswith('_0_8bit.fil')):
        filfiles.append(filfile)

filfiles = np.array(filfiles)
filespd = pd.DataFrame(filfiles, columns=['filename'])
filespd['mjd'] = pd.to_numeric(filespd['filename'].str.split('_', expand=True)[1])
filespd.sort_values(by='mjd', inplace=True)

candfiles = []

for candfile in sorted(os.listdir(canddir)):
    #print(candfile)
    if (candfile.endswith('_' + beam + '.cand')):
        if os.stat(os.path.join(canddir, candfile)).st_size > 0:
            print("Processing file %s" % candfile) 
            candfiles.append(candfile)


candfiles = np.array(candfiles)
candspd = pd.DataFrame(candfiles, columns=['candfile'])

candspd['date'] = candspd['candfile'].str.split('_', expand=True)[0]
candspd['date'] = candspd['date'].str.replace('-', 'T')
candspd['date'] = candspd['date'].str.replace('2018T01T', '2018-01-')

print(candspd.head(10))

dates = candspd['date'].values.tolist()
candspd['mjd'] = Time(dates, format='isot', scale='utc').mjd
candfils = []

for idx, row in candspd.iterrows():
    filemjds = filespd[filespd['mjd'] <= row['mjd']]
    filemjds = filemjds.sort_values(by='mjd', ascending=False)
    filfile = filemjds.iloc[0].filename
    #print(filfile)
    candfils.append(filfile)

candspd = candspd.drop(['mjd'], axis=1)
candspd = candspd.drop(['date'], axis=1)
candspd['filfile'] = candfils
#candspd["test"] = ""
print(candspd.head(10))

candspd.to_csv(os.path.join(canddir, 'for_dedisp.dat'), sep='\t', index=False, header=False)

