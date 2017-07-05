/* file: 	onsetsDS.i
*  date: 	4/17/2017
*  author:	Conner Brown
*  brief:	swig interface file for onsetsDS
*/

%module onsetsDS
%{
//put onsetsdshelpers.c functions (or headers) here...
#include "onsetsdshelpers.h"
/*
#include "onsetsDS/src/onsetsds.h"
#include <usr/include/stdlib.h>
#include <usr/include/sndfile.h>
#include <fftw3.h>
*/

%}

//and here...
%include "onsetsdshelpers.h"
/*
%include "onsetsDS/src/onsetsds.h"
%include <stdlib.h>
%include <sndfile.h>
%include <fftw3.h>
*/
