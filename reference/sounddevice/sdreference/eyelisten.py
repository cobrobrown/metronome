# file:        eyelisten.py
# author:      Conner Brown
# date:        4/29/2017
# update:      4/29/2017
# brief:       perform light show in realtime with mic input

import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
from scipy.fftpack import fft
import pyfirmata as pf
import time


def play():
    #initialize board
    board=None
    try:
        board=pf.Arduino('/dev/ttyACM0')
    except:
        try:
            board=pf.Arduino('/dev/ttyACM1')
        except:
            print "Board failed to initialize"
            return    
    if board is not None:
        pin9=board.get_pin('d:9:p')
        pin5=board.get_pin('d:5:p')
        pin6=board.get_pin('d:6:p')
        print "Board initialized"
    else:
        print "Board failed to initialize"
        return

    # constants
    i=0
    fs = 44100
    duration = 1024.0
    # generate A weighting matrix
    freqs=np.ones(int(duration))*fs/duration/2.0
    Aweight=(12194**2)*freqs**4/((freqs**2+20.6**2)*(freqs**2+12194**2)*((freqs**2+107.7**2)*(freqs**2+737.9**2))**(1/2.0))
    
    #listen and display values
    while 1:
        #sound capture
        myrecording = sd.rec(int(duration), samplerate=fs, channels=1)
        sd.wait()
        
        #fft
        length=len(myrecording)
        myrec=np.array(myrecording)
        myrec=np.transpose(myrec)
        yf=fft(myrec)
        #xf=np.linspace(0.0,fs/2.0, length//2)
        yf=np.transpose(yf)
        spec=2.0/length*(np.abs(yf[0:length/2])**2)
        weightedspec=spec*Aweight
        
        
        #led values
        loval=np.sum(weightedspec[0:20])
        mdval=np.sum(weightedspec[10:30])
        hival=np.sum(weightedspec[20:])

        #write to pins
        #many much flicker happens in loval, mostly ambient noise
        if loval<.01:
            loval=0
        pin9.write(loval)
        pin5.write(mdval)
        pin6.write(hival)


def main():
    play()

if __name__ == '__main__':
    main()
