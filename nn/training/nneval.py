"""
	This file contains loss evaluations functions
	
	Author: Matthew Levine
	Date: 02/02/2015
"""
from feedforward import feedforward
from training.nntest import nntest

def nneval( nn, loss, train_x, train_y, val_x=None, val_y=None):
	"""  Evaluates performance of neural network
	
		Returns an updated loss structure
	"""
	nargin = 4 + (val_x is not None) + (val_y is not None)
	assert nargin == 4 or nargin == 6, "Wrong number of arguments"
	
	nn.testing = 1
	# training performance
	nn = nn.copy() # don't change the input nn
	# print('starting')
	feedforward( nn, train_x, train_y )
	loss.train.e.append( nn.L )
	# print("stopping")
	# exit()
	
	# validation performance
	if nargin == 6:
		nn = feedforward(nn,val_x,val_y)
		loss.val.e.append( nn.L )
		
	nn.testing = 0
	
	# calc miscalssification rate if softmax
	if nn.output == 'softmax':
		(er_train, _) = nntest(nn,train_x,train_y)
		loss.train.e_frac.append( er_train )
		
		if nargin == 6:
			(er_val,_) = nntest(nn,val_x,val_y)
			loss.val.e_frac.append( er_val )
			
			
	return loss