# file:     iothreading.py
# author:   Conner Brown
# date:     5/10/2017
# update:   6/6/2017
# brief:    implement input and output capture with threading. perform primary analysis: onset detection, filtering
# status:   add deconvolution filter, improve onset detection algorithm, python style guide

import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import time
import threading
from Queue import Queue
from ctypes import POINTER, c_ubyte, c_void_p, c_ulong, cast
# From https://github.com/Valodim/python-pulseaudio
from pulseaudio.lib_pulseaudio import *

#global variables
c = threading.Condition()
start = 0.0
frame_size = 2048
out_frame = np.zeros(frame_size)
in_frame = np.zeros(frame_size)
sync = False
count_trigger = Queue()

class clicktrack(threading.Thread):
    def __init__(self,name,bpm):
        threading.Thread.__init__(self)
        self.name=name
        self.bpm=int(bpm)
        self.click=np.ones(512)
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
        global out_frame
        global in_frame
        global sync
        global count_trigger
        i = 0
        fs = 44100
        duration = frame_size*1.0
        loud = 0

        #wait for the sync trigger
        c.acquire()
        while not sync:
            c.wait()
        c.release()

        while sync:
            if not count_trigger.empty():
                print "TRIGGERED A LA COUNT"
                break
            #sound capture
            c.acquire()
            in_frame = sd.rec(int(duration), samplerate=fs, channels=1)
            sd.wait()
            c.notify_all()
            c.release()
#############
            #filter input by output

            #replace rudimentary onset detection with algorithmic onset detection
            #display offset of input from output
#############
            loud=np.sum(in_frame**2)
            if loud>0.1:
                c.acquire()
                offset=start-time.time()
                print 'offset %f' % (offset)
                c.release()

class audio_output(threading.Thread,object):

    def __init__(self, name, sink_name, rate):
        threading.Thread.__init__(self)
        self.name=name        
        self.sink_name = sink_name
        self.rate = rate

        # Wrap callback methods in appropriate ctypefunc instances so that the Pulseaudio C API can call them
        self._context_notify_cb = pa_context_notify_cb_t(self.context_notify_cb)
        self._sink_info_cb = pa_sink_info_cb_t(self.sink_info_cb)
        self._stream_read_cb = pa_stream_request_cb_t(self.stream_read_cb)

        # stream_read_cb() puts samples
        self._samples = Queue()

        # Create the mainloop thread and set our context_notify_cb
        # method to be called when there's updates relating to the
        # connection to Pulseaudio
        _mainloop = pa_threaded_mainloop_new()
        _mainloop_api = pa_threaded_mainloop_get_api(_mainloop)
        context = pa_context_new(_mainloop_api, 'output_capture')
        pa_context_set_state_callback(context, self._context_notify_cb, None)
        pa_context_connect(context, None, 0, None)
        pa_threaded_mainloop_start(_mainloop)

    def __iter__(self):
        while True:
            yield self._samples.get()

    def context_notify_cb(self, context, _):
        state = pa_context_get_state(context)

        if state == PA_CONTEXT_READY:
            print "Pulseaudio connection ready..."
            # Connected to Pulseaudio. Now request that sink_info_cb
            # be called with information about the available sinks.
            o = pa_context_get_sink_info_list(context, self._sink_info_cb, None)
            pa_operation_unref(o)

        elif state == PA_CONTEXT_FAILED :
            print "Connection failed"

        elif state == PA_CONTEXT_TERMINATED:
            print "Connection terminated"

    def sink_info_cb(self, context, sink_info_p, _, __):
        if not sink_info_p:
            return

        sink_info = sink_info_p.contents
        print '-'* 60
        print 'index:', sink_info.index
        print 'name:', sink_info.name
        print 'description:', sink_info.description

        if sink_info.name == self.sink_name:
            # Found the sink we want to monitor for peak levels.
            # Tell PA to call stream_read_cb with peak samples.
            samplespec = pa_sample_spec()
            samplespec.channels = 1
            samplespec.format = PA_SAMPLE_U8
            samplespec.rate = self.rate

            pa_stream = pa_stream_new(context, "output capture", samplespec, None)
            pa_stream_set_read_callback(pa_stream,
                                        self._stream_read_cb,
                                        sink_info.index)
            pa_stream_connect_record(pa_stream,
                                    sink_info.monitor_source_name,
                                     None,0)

    def stream_read_cb(self, stream, length, index_incr):
        data = c_void_p()
        pa_stream_peek(stream, data, c_ulong(length))
        data = cast(data, POINTER(c_ubyte))
        for i in xrange(length):
            # When PA_SAMPLE_U8 is used, samples values range from 0 to 255 because the underlying audio data is signed
            self._samples.put(data[i]-127)
        #print 'Queue size: %5d \r' % self._samples.qsize(), sys.stdout.flush()        
        pa_stream_drop(stream)
        if self._samples.qsize() > 4000:
            while not self._samples.empty():
                self._samples.get()


def main():
    # extra includes for visualization
    import matplotlib.pyplot as plt
    import math
    # shared variables, use condition variable c to lock/unlock
    global out_frame
    global in_frame
    global start
    global sync
    # test variable
    global count_trigger
    print "Enter any key to begin iothreading.py: "
    bpm = raw_input()
    #set up audio output
    SINK_NAME = 'alsa_output.pci-0000_00_1b.0.analog-stereo'
    SAMPLE_RATE = 44100
    #start offset, audio_output threads
    output = audio_output("audio output",SINK_NAME,SAMPLE_RATE)
    off = offset()
    output.start()
    off.start()
    #gather frames of output
    trigger = 0 
    count = 0
    elapsed = 0.0
    for sample in output:
        #synchronize out_frame with in_frame (sub millisecond operation)
        if not sync:
            print "-----------Starting sync------------"
            c.acquire()
            sync = True
            c.notify_all()
            c.release()
        if trigger < frame_size:
            out_frame[trigger]=sample/127.0
            trigger+=1
        else:
            #now we have a full frame (1024 samples)
            #rudimentary onset detection
            
            #if np.sum(out_frame**2) > 0.1:
            elapsed = time.time() - start
            print "elapsed %.4f" % elapsed
            c.acquire()
            start = time.time()
            c.notify_all()
            c.release()
            trigger = 0
            count += 1
        #test stopping variable
        if count > 10:
            #print "she is a total betch"
            count_trigger.put(1)
            break
    time.sleep(1)


    #normalize in_frame, out_frame -1 to 1
    inmaxi=np.abs(np.max(in_frame[:,0]))   
    inmini=np.abs(np.min(in_frame[:,0]))
    indiff = 0.0
    if inmaxi>inmini:
        indiff=-(inmaxi-inmini)
    else:
        indiff=inmini-inmaxi
    in_frame[:,0]=in_frame[:,0]+indiff/2.0
    in_frame[:,0]=in_frame[:,0]/np.max(in_frame[:,0])

    outmaxi=np.abs(np.max(out_frame))
    outmini=np.abs(np.min(out_frame))
    outdiff = 0.0
    if outmaxi>outmini:
        outdiff=-(outmaxi-outmini)
    else:
        outdiff=outmini-outmaxi
    out_frame=out_frame+outdiff/2.0
    out_frame=out_frame/np.max(out_frame)

    #fft of in_frame, out_frame
    in_f = np.fft.fft(in_frame[:,0])
    in_spec = 2.0/len(in_f)*np.abs(in_f[0:len(in_f)/2])**2
    in_freqs = np.arange(len(in_spec))*SAMPLE_RATE/len(in_spec)/2.0
    out_f = np.fft.fft(out_frame)
    out_spec = 2.0/len(out_f)*np.abs(out_f[0:len(out_f)/2])**2
    out_freqs = np.arange(len(out_spec))*SAMPLE_RATE/len(out_spec)/2.0

    #show some in_f, out_f
#    print in_f[0:len(in_f)/4]
#    print 'IN'*30
#    print out_f[0:len(out_f)/4]
#    print 'OUT'*20

    #correlation of out_frame and in_frame
    corr = np.correlate(out_frame,in_frame[:,0],"full")
    # in_frame, out_frame time series plots
    plt.figure()
    plt.title("in_frame")
    plt.plot(in_frame[:,0])
    plt.figure()    
    plt.title("out_frame")
    plt.plot(out_frame)    
    
    #in_frame, out_frame frequency spectrum plots
    plt.figure()
    plt.title("in_frame fft")
    plt.plot(in_freqs,in_spec)

    plt.figure()
    plt.title("out_frame fft")
    plt.plot(out_freqs,out_spec)

    #test filter
    envir_f = in_f/out_f
    envir_spec = 2.0/len(envir_f)*np.abs(envir_f[0:len(envir_f)/2])**2
    plt.figure()
    plt.title("fft environment")
    plt.plot(in_freqs,envir_spec)
    
    envir = np.fft.ifft(envir_f)
    plt.figure()
    plt.title("inverse fft = environment")
    plt.plot(envir)
    sd.play(envir.real,44100)
    #check envir imaginary components
    print "ENVIR"*10
    print envir[0:100]

    # correlation plot
    #plt.figure()
    #plt.title("full correlation in/out")
    #plt.plot(corr)
    
    plt.show()



    #determine bpm of output
        #use onsets on output
        #count spaces in between onsets (with some case handling/filtering)
    #set start to 0 phase of output bpm using onset detection
#####
    output.join()
    off.join()

if __name__ == '__main__':
    main()
