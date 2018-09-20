from glob import glob
from numpy import genfromtxt, int32, savetxt
import sys
from os.path import join
from os import stat
datadir = sys.argv[2]
beams = int(sys.argv[1])

files = 0

while(True):
    files = 0
    filelist=glob(join(datadir, '10.17.*'))
    for filename in filelist:
        if (stat(filename).st_size != 0):
            files = files+1      
    
    if files == beams:
        break;

startepoch=0;
startsec=0;
startframe=0;

starttime = [[0,0,0]]

for filename in filelist:
    startdata = genfromtxt(filename, dtype=int32)
#    print(startdata[0])
#    print(startdata[1])
#    print(startdata[2])

    starttime.append([startdata[0], startdata[1], startdata[2]])

    #if (startdata[0] > startepoch):
    #    startepoch = startdata[0]
    #    startsec = startdata[1]
    #    startframe = startdata[2]
    #elif (startdata[1] > startsec):
    #    startepoch = startdata[0]
    #    startsec = startdata[1]
    #    startframe = startdata[2]
    #    elif (startdata[2] > startframe): 
    #        startepoch = startdata[0]
    #        startsec = startdata[1]
    #        startframe = startdata[2]

    #    print('%d, %d, %d\n' % (startepoch, startsec, startframe))
    
    #print('\n\n')

#Add extra ~5.4 second

starttime = sorted(starttime, key = lambda x: (x[0], x[1], x[2]), reverse=True)

startepoch = starttime[0][0];
startsec = starttime[0][1];
startframe = starttime[0][2];

startframe = startframe + 50000
if startframe >= 250000:
    startsec = startsec + 27
    startframe = startframe % 250000

print("That's what goes into the file:")
print(startepoch)
print(startsec)
print(startframe)
       
savetxt(join(datadir, 'start_now.dat'), [startepoch, startsec, startframe], fmt='%d', delimiter='\t')
