"""
	This file contains utility functions for working with numpy matrices
	and vectors
	
	Author: Matthew Levine
	Date: 01/17/2015
"""

import sys
from math import sqrt
from inspect import getargspec as args_of
from numpy import shape, array, zeros
import logging
import time

verbose = True
logging_on = False
elapsed = time.time()

def flags():
	""" Returns the module level flags """
	return {'verbose':verbose,'logging_on':logging_on}


def udim(x):
	""" Returns the dimension of the matrix form of a vector.

		This function is not a fast way to do this, so it should only be
		used for clarity or conciseness where speed is not pertinant.
	"""
	dim = sqrt(x.shape[0])

	assert int(dim) == dim and dim > 1, "Can't rotate non-square matrix or matrix smaller than rank 2"

	return int(dim)
	
def Overrides(interface_class):
	""" Annotates a method as overriding from its super class """
	def overrider(method):
		assert method.__name__ in dir(interface_class), 'Method '+str(method)+' does not inherit from parent'

		args0,args1 = args_of(method), args_of(interface_class.__dict__[method.__name__])
		assert len(args0.args) == len(args1.args) and \
			(args0.keywords is None) == (args1.keywords is None) and \
			(args0.varargs is None) == (args1.varargs is None), "Method signature does not match its parent's"
		
		return method
	return overrider


def deprecated(function):
    """ Marks a function as intending to not be used in final production.
		Such functions only exist for testing code.
	"""
    def inner(*args, **kwargs):
        disp("Warning: Deprecated function \"%s\" is not recommended in production code" % function.__name__)
        return function(*args, **kwargs)
    inner.__name__ = function.__name__
    inner.__doc__ = function.__doc__
    inner.__dict__.update(function.__dict__)
    return inner

	
def disp(*words,verbose_l = False, startime=0, stoptime=0):
	""" Outputs the text if either the modular level or supplied verbosity
		flag is true. By default, the supplied flag is false.
		
		If startime is true, starts timing the current operation.
		If stoptime is true, logs time since last clock start.
		
		This function might do other things too (it logs, e.g). It should
		probably except error messages and warnings, also. For this reason,
		it is (relatively) slowish if any level of verbosity is enabled. If not,
		it returns pretty quickly, so can be called safely in non-performance-
		critical code with verbosity disabled unilaterally at production.
	"""
	global verbose, logging_on, elapsed
	if verbose or verbose_l: 
		print(*words)
	else:
		return 
		
	if not logging_on:
		logging.basicConfig(filename='nn.log',level=logging.DEBUG)
		logging_on = True
		logging.basicConfig(format='%(asctime)s %(message)s')
		logging.info("Started logging session")
		
	if stoptime == 1:
		dt = 'Elapsed time for last operation: '+str(time.time()-elapsed)
		logging.info(dt)
		print(dt)
	if startime == 1:
		elapsed = time.time()
		
	logging.info(' '.join([str(s) for s in words])+'\n')

	
def addBias(A):
	""" Adds a bias layer to A.
		
		Relative to other ways of doing this in numpy, it's pretty fast, 
		though I'd consider shoving it C if the memory management isn't a
		nightmare. Bottom line, you can count on this function be certainly
		not its implementation
	"""
	B = zeros((A.shape[0],A.shape[1]+1))
	B[:,1:] = A
	B[:,0]  = 1
	return B	

def addPenalty(A):
	""" Adds an empty layer to A """
	B = zeros((A.shape[0],A.shape[1]+1))
	B[:,1:] = A
	return B

	
@deprecated
def size(x):
	return shape(x)
	
@deprecated
def add(A,B):
	return array([a.tolist() + b.tolist() for a,b in zip(A,B)])

@deprecated
def addpath(path): 
	sys.path.append(path)
	
def get_command(usage):
	""" Returns the first flag on the command line """
	if len(sys.argv) < 2:
		disp(usage)	
		return None
		
	return sys.argv[1]
	
def get_flag_value(flag,type,default):
	if not '--'+flag in sys.argv[1:]:
		return default
	
	index = sys.argv.index('--'+flag)
	if len(sys.argv) > index:
		try:
			default = type(sys.argv[index+1])
		except TypeError:
			disp("Batch size must be of type",type)
			return None
	
	return default

	
if __name__ == '__main__':
	class Foo:
		def foo(x='hello world',*args,**kwargs):pass
	class Bar(Foo):
		@Overrides(Foo)
		def foo(x='hello worly',*args,**kwargs):pass
		
	from numpy import ones
	
	a = array([[1,2,3],[4,5,6]])
	print(addBias(a))
	
	print(add( ones( (a.shape[0],1) )), a)