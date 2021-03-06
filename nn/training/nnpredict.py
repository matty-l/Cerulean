"""
	This file contains basic neural network prediction utlities
	
	Author: Mathew Levine
	Date: 02/02/2015
"""

from feedforward import feedforward
from numpy import zeros, shape

size = lambda x:shape(x)


def nnpredict(nn,x,ff=1):
	""" Propogates X through the nn using the current weights in the system,
		and returns its estimates based on the last layer of the network, i.e,
		returns the index of the most activated layer after a pass of X.
	"""
	nn.testing = 1
	nn = nn.copy()
	# if ff:
	feedforward( nn, x, zeros( (size(x)[0], nn.size[-1] ) ) )
	nn.testing = 0
	
	i = max( nn.a.keys() )
	return nn.a[i].argmax(1)
	