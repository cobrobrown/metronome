# file: 	setup.py
#  date: 	4/17/2017
#  author:	Conner Brown
#  brief:	setup file for building onsetsDS module
#
from distutils.core import setup, Extension

## sources: onsetsds.c, onsetsdshelpers.c, onsetsDS.i
onsetsDS_modules = Extension('_onsetsDS',sources=['onsetsDS/src/onsetsds.c','onsetsDS/src/onsetsdshelpers.c','onsetsDS.i'])


## headers: onsetsdshelpers.h 
setup(name='onsetsDS',ext_modules=[onsetsDS_modules],headers=['onsetsDS/src/onsetsdshelpers.h'], py_modules=["onsetsDS"])
