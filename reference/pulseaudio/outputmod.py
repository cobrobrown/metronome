# file:     outputmod.py
# author:   Conner Brown
# date:     5/10/2017
# update:   5/10/2017
# brief:    capture output audio data for use in other programs


from Queue import Queue
from ctypes import POINTER, c_ubyte, c_void_p, c_ulong, cast
import time

# From https://github.com/Valodim/python-pulseaudio
from pulseaudio.lib_pulseaudio import *

class AudioOutput(object):

    def __init__(self, sink_name, rate):
        self.sink_name = sink_name
        self.rate = rate

        # Wrap callback methods in appropriate ctypefunc instances so
        # that the Pulseaudio C API can call them
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
        context = pa_context_new(_mainloop_api, 'peak_demo')
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
        if self._samples.qsize() > 2000:
            while not self._samples.empty():
                self._samples.get()

#### Sample Main for capture and analysis
'''
def main():
    import numpy as np
    import matplotlib.pyplot as plt
    SINK_NAME = 'alsa_output.pci-0000_00_1b.0.analog-stereo'  
    SAMPLE_RATE = 44100
    MAX_SAMPLE_VALUE = 127
    monitor = AudioOutput(SINK_NAME, SAMPLE_RATE)
    trigger=0
    count=0
    start=0.0
    elapsed=0.0
    frame=np.zeros(1024)
    for sample in monitor:
        if trigger < 1024:
            frame[trigger]=sample
            trigger+=1
        else:
            elapsed=time.time()-start
            print elapsed
            start=time.time()
            trigger=0
            count+=1
        if count>10:
            break
    frame0=np.zeros(len(frame)*2)  #zero-padding    
    frame0[len(frame)/2:3*len(frame)/2]=frame
    framef=np.fft.fft(frame0)
    framespec=2.0*np.abs(framef[0:len(framef)/2])**2
    framefreqs=np.arange(len(framef)/2)*float(SAMPLE_RATE/len(frame0))
    plt.figure()
    plt.title('single frame fft')
    plt.plot(framefreqs,framespec)
    plt.show()

if __name__ == '__main__':
    main()
'''
