"""
	This file contains utility functions for working with numpy matrices
	and vectors
	
	Author: Matthew Levine
	Date: 01/17/2015
"""

import sys
from math import sqrt
from inspect import getargspec as args_of
from numpy import shape, array

def udim(x):
	""" Returns the dimension of the matrix form of a vector """
	dim = sqrt(x.shape[0])

	assert int(dim) == dim and dim > 1, "Can't rotate non-square matrix or matrix smaller than rank 2"

	return int(dim)


def addpath(path):
	sys.path.append(path)
	
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
	
size = lambda x:shape(x)

add = lambda A,B: array([a.tolist() + b.tolist() for a,b in zip(A,B)])
	
if __name__ == '__main__':
	class Foo:
		def foo(x='hello world',*args,**kwargs):pass
	class Bar(Foo):
		@Overrides(Foo)
		def foo(x='hello worly',*args,**kwargs):pass