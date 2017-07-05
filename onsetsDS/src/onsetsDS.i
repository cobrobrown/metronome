/* file: 	onsetsDS.i
*  date: 	4/17/2017
*  author:	Conner Brown
*  brief:	swig interface file for onsetsDS
*/

%module onsetsDS
%{
//put onsetsdshelpers.c funcitons (or headers) here...

#include <stdlib.h>
#include <sndfile.h>
#include <fftw3.h>
#include "onsetsds.h"

#include "onsetsdshelpers.h"
%}

//and here...
%include <stdlib.h>
%include <sndfile.h>
%include <fftw3.h>
%include "onsetsds.h"

%include "onsetsdshelpers.h"

