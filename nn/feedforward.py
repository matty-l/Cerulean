"""
	This file contains the feed forward part of the mlp
	
	Author: Matthew Levine
	Date: 02/02/2015
"""

from numpy import shape, array, ones, mean, sum, log, exp, max
from numpy.random import random as rand

from utils.utils import addBias

# ------------------------------------------ #
# Notes on performance:						 #
# Using utils.utils.add: 11.2444s			 #
# Using utils.utils.addBias: 4.4405s		 #
# ------------------------------------------ #

def feedforward(nn,x,y):
	""" Performs a feedforward pass.
	
	If this function throws an exception, it's almost definately because of
	dimension mismatch between the weight matrices and x. Check to make sure
	that the architecture you described in nnsetup actually fits with the 
	size of the input set.
	
		Feeds forward the neural network to update layer activations, error, and loss
	"""
	
	n = nn.n
	m = x.shape[0]

	x = addBias(x)
	nn.a[0] = x
	
	# feed forward pass
	for i in range(1,n-1):
		nn.a[i] = nn.activation_function_impl.feedforward(nn.a[i-1],nn.W[i-1])			
			
		# dropout
		if nn.dropoutFraction > 0:
			if nn.testing:
				nn.a[i] = nn.a[i] * (1-nn.dropoutFraction)
				
			else:
				nn.dropOutMask[i] = (rand(nn.a[i].shape)>nn.dropoutFraction)
				nn.a[i] = nn.a[i] * nn.dropOutMask[i]
								
		# add the bias term
		nn.a[i] = addBias(nn.a[i])
		
	nn.a[n-1] = nn.output_function.feedforward(nn.a[n-2],nn.W[n-2])

	# error and loss
	nn.e = y - nn.a[n-1]
	
	nn.L = nn.output_function.evaluate_loss( nn.e, m, nn.a[n-1], y )
	
	
	
if __name__ == '__main__':
	from scipy.io import loadmat
	from scipy.misc import toimage
	from nnsetup import nnsetup
	
	print("Loading data...")
	result = loadmat('mnist_uint8.mat')
	
	nn = nnsetup([784,100,10])
	x = result['train_x'].astype(float) / 255
	y = result['train_y'].astype(float)

	print("Propogating")
	nnff(nn,x,y)
	
	level = 'third'
	
	if level == 'first':
		first_activations = nn.a[0][0,1:]
		print(first_activations.shape)
		# print(first_activations)
		toimage(first_activations.reshape((28,28))).show()
	elif level == 'second':
		second_activations = nn.a[1][0,1:]
		print(second_activations.shape)
		# print(second_activations)
		toimage(second_activations.reshape((10,10))*255).show()
	elif level == 'third':
		from testfunc import testfunc
		x = testfunc(nn.a[1], nn.W[1])
		for val in x[0]:
			print(float(val))	
		# second_activations = nn.a[2][0,1:]
		# print(size(second_activations))
		# print(second_activations)
		# print(nn.W[1])
		# toimage(second_activations.reshape((10,10))*255).show()
		
		
	