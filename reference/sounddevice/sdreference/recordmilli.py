# file:        recordmilli.py
# author:      Conner Brown
# date:        4/29/2017
# update:      4/29/2017
# brief:       use sounddevice module to record milliseconds of input and perform some analysis to verify


import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import matplotlib.pyplot as plt
from scipy.fftpack import fft


#sound capture
fs=44100
duration=1024/44100.0
myrecording = sd.rec(int(duration*fs), samplerate=fs, channels=1)
print len(myrecording)
print "Recording Audio"
sd.wait()
print "Audio recording complete, play audio"
sd.play(myrecording, fs)
sd.wait()
print "play audio complete"

print len(myrecording)

#fft
length=len(myrecording)
myrec=np.array(myrecording)
myrec=np.transpose(myrec)
yf=fft(myrec)
xf=np.linspace(0.0,fs/2.0, length//2)
yf=np.transpose(yf)
spec=2.0/length*np.abs(yf[0:length/2])

print np.max(spec)
#plt.plot(xf,spec)
#plt.show()
