# File:		seefreqs.py
# Date: 	4/24/2017
# Author: 	Conner Brown
# Brief: 	capture audio with Alsa, plot the fft in animation style

from __future__ import division
import alsaaudio, time, audioop
import numpy as np
from scipy.io import wavfile
from scipy.fftpack import fft
import matplotlib.pyplot as plt
import struct
import decodehex

def capture():
    inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NONBLOCK)

    channels=1
    samplerate=44100
    periodsize=160


    inp.setchannels(channels)
    inp.setrate(samplerate)
    inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)

    inp.setperiodsize(periodsize)


    ## Analyze data from input....first convert it to 16bit int

    i=0
    l,data = inp.read()
    while not data:
        l,data=inp.read()        
    print len(data)
    print type(data)
    print l
    print data
    print "---------------------NEWDATA------------------"
    #print int(data[0],16)
    #print data.decode('utf-8')
    #newdata=struct.unpack('<h',data)
    #newdata=wavfile.read(data)
    newdata=decodehex.tointarray(data,l)
    
    print newdata
    return newdata



## Example analysis, plotting live fft


#while i<1:
#    l,data = inp.read()
#    print len(data)
#    print l
#    if data:
#        y=fft(data)
#        spec=2.0/len(y)*np.abs(y[0:len(y)//2])
#        freqs=np.linspace(0,samprate/2,len(spec))

#        plt.plot(freqs,spec)
#        plt.show()
#    i=i+1
#    time.sleep(3)
