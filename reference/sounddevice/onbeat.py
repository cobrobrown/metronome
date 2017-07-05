# file:        onbeat.py
# author:      Conner Brown
# date:        5/8/2017
# update:      5/8/2017
# brief:       display the time difference in a user's playing from the set bpm. uses threading and shared variables.

import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import time
import threading
import sys

# global variables
c = threading.Condition()
start=0.0

class clicktrack(threading.Thread):
    def __init__(self,name,bpm):
        threading.Thread.__init__(self)
        self.name=name
        self.bpm=int(bpm)
        self.click=np.ones(512)#np.arange(512)/512.0
        self.fs=44100

    def run(self):
        bpminseconds=60.0/self.bpm
        global start
        elapsed=0.0
        while True:
            elapsed=time.time()-start
            if elapsed>bpminseconds:
                print 'X'*10
                #sd.play(self.click,self.fs)
                #sd.wait()
                c.acquire()
                start=time.time()
                c.notify_all()
                c.release()
            time.sleep(bpminseconds-bpminseconds*.9)

class offset(threading.Thread):
    def __inti__(self,name):
        threading.Thread.__init__(self)
        self.name=name

    def run(self):
        # constants
        global start
        i=0
        fs = 44100
        duration = 1024.0
        loud=0  

        while True:
            #sound capture
            myrecording = sd.rec(int(duration), samplerate=fs, channels=1)
            sd.wait()
            loud=np.sum(myrecording**2)
            if loud>0.1:
                c.acquire()
                offset=start-time.time()
                print ' %f \r' % (offset)
                c.release()

def main():
    print "Input a bpm as an integer"
    bpm=raw_input()
    off=offset()
    click=clicktrack("click",bpm)
    off.start()
    click.start()
    off.join()
    click.join()

if __name__ == '__main__':
    main()
