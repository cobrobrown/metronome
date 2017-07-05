# file:        multiproctest.py
# author:      Conner Brown
# date:        5/9/2017
# update:      5/9/2017
# brief:       try python multiprocessing (to eschew c++ even though its faster). implement onbeat.py with multiprocessing
# status:      NON_OPERATIONAL; sounddevice does not open inputstream
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import time
from multiprocessing import Process, Queue

def clicktrack(q,bpm):
    print "clicktrack begin"
    click=np.ones(512)
    fs=44100
    bpminseconds=60.0/bpm
    start=0.0
    elapsed=0.0
    while True:
        elapsed=time.time()-start
        if elapsed>bpminseconds:
            print elapsed
            #sd.play(click,fs)
            #sd.wait()
            start=time.time()
            q.put(start)

def offset(q):
    print "offset begin"
    fs=44100
    duration=1024.0
    loud=0
    beat=0

    while True:
        myrecording=sd.rec(int(duration),samplerate=fs,channels=1)
        sd.wait()
        loud=np.sum(myrecording**2)
        if loud>0.1:
            if not q.empty():
                beat=q.get()
            offset=beat-time.time()
            print offset

if __name__ == '__main__':
    print "opening input stream once here"
    testrec=sd.rec(1024,samplerate=44100,channels=1)
    sd.wait()
    print "Input a bpm as an integer"
    bpm=int(raw_input())
    myq=Queue()
    clickproc=Process(target=clicktrack,args=(myq,bpm,))
    offsetproc=Process(target=offset,args=(myq,))
    clickproc.start()
    offsetproc.start()
    clickproc.join()
    offsetproc.join()
