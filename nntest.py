"""
	This file contains functions to test an mlp
	
	Author: Matthew Levine
	Date: 02/02/2015
"""
from numpy import max,shape
from nnpredict import nnpredict

size = lambda x:shape(x)

__verbose__ = 1

def nntest(nn,x,y):
	""" Tests the neural network
	"""
	labels = nnpredict(nn,x)
	expected = y.argmax(1)
	bad = [ label != expect for label,expect in zip(labels,expected) ]
	if __verbose__:
		print('Misclasifciation: ',sum(bad)/size(x)[0])
	return sum(bad) / size(x)[0], bad