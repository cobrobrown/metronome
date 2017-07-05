# File:		decodehex.py
# Date: 	4/24/2017
# Author: 	Conner Brown
# Brief: 	decode hexadecimal alsa output

import numpy as np
import struct

def tointarray(data,l):
    fmt=len(data)
    fmt=str(fmt)+'B'    
    newdata=struct.unpack(fmt,data)
    np.array(newdata)
    #combine bits according to format
    framesize=len(data)/l
    decdata=np.zeros(l)
    x=np.array([1,2,3,4])
    for i in range(0,l):
        tempsum=0
        #for j in range(0,framesize):
            #tempsum=tempsum+newdata[framesize*i+j]*(2**(4*(framesize-j-1)
        decdata[i]=newdata[2*i]+newdata[2*i+1]*256-32768.0
        #only for 16 bit
        #decdata[i]=tempsum
    return decdata
