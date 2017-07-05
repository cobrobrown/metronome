# File:		shout.py
# Date: 	4/24/2017
# Author: 	http://stackoverflow.com/questions/1936828/how-get-sound-input-from-microphone-in-python-and-process-it-on-the-fly
# Brief: 	use Alsa for Python to capture floating point audio data


##
## The script opens an ALSA pcm for sound capture. Set
## various attributes of the capture, and reads in a loop,
## Then prints the volume.
##
## To test it out, run it and shout at your microphone:

import alsaaudio, time, audioop

# Open the device in nonblocking capture mode. The last argument could
# just as well have been zero for blocking mode. Then we could have
# left out the sleep call in the bottom of the loop
inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE,alsaaudio.PCM_NONBLOCK)

# Set attributes: Mono, 44100 Hz, 16 bit little endian samples
inp.setchannels(1)
inp.setrate(44100)
inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)

# The period size controls the internal number of frames per period.
# The significance of this parameter is documented in the ALSA api.
# For our purposes, it is suficcient to know that reads from the device
# will return this many frames. Each frame being 2 bytes long.
# This means that the reads below will return either 320 bytes of data
# or 0 bytes of data. The latter is possible because we are in nonblocking
# mode.
inp.setperiodsize(160)

# Use average to threshold shout detection
avgnum=1
avg=0
datamax=0
while True:
    # Read data from device
    l,data = inp.read()
    if l:
	datamax=audioop.max(data, 2)
	avg=(avg*avgnum+datamax)/(avgnum+1)
	avgnum=avgnum+1
	if avgnum>1000000:
	    avg=datamax
	    avgnum=1
	if datamax>2.5*avg: #or 4000 for 44100 Hz 
	    print "SHOUT #",avgnum

