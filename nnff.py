"""
	This file contains the feed forward part of the mlp
	
	Author: Matthew Levine
	Date: 02/02/2015
"""

from numpy import shape, array, ones, mean, sum, log, exp, max
from numpy.random import random as rand

from tanh_opt import tanh_opt
from sigm import sigm
from softmax import softmax

from utils import add, size

def nnff(nn,x,y):
	""" Performs a feedforward pass
	
		Feeds forward the neural network to update layer activations, error, and loss
	"""
	
	n = nn.n
	m = size(x)[0]

	x = add(ones((m,1)),x)
	nn.a[0] = x
	
	# feed forward pass
	for i in range(1,n-1):
		if nn.activation_function == 'sigm':
			# calculate the unit's outputs (including the bias term)
			nn.a[i] = sigm(nn.a[i-1].dot(nn.W[i-1].transpose()))
		elif nn.activation_function == 'tanh_opt':
			try:
				nn.a[i] = tanh_opt(nn.a[i-1].dot(nn.W[i-1].transpose()))
			except Exception as e:
				raise e # this seems silly, but sometimes it's useful to error-check here
			
			
		# dropout
		if nn.dropoutFraction > 0:
			if nn.testing:
				nn.a[i] = nn.a[i] * (1-nn.dropoutFraction)
				
			else:
				nn.dropOutMask[i] = (rand(size(nn.a[i]))>nn.dropoutFraction)
				nn.a[i] = nn.a[i] * nn.dropOutMask[i]
								
		# add the bias term
		nn.a[i] = add( ones((m,1)), nn.a[i] )
		
	nn.a[n-1] = nn.output_function.feedforward(nn.a[n-2],nn.W[n-2])
	# if nn.output == 'sigm':		
		# nn.a[n-1] = sigm(nn.a[n-2].dot(nn.W[n-2].transpose()))
	# elif nn.output == 'softmax':
		# nn.a[n-1] = softmax(nn.a[n-2].dot(nn.W[n-2].transpose()))

	# error and loss
	nn.e = y - nn.a[n-1]
	
	nn.L = nn.output_function.evaluate_loss( nn.e, m, nn.a[n-1], y )
	# if nn.output == 'sigm':
		# nn.L = 1/2 * sum(sum(nn.e * nn.e)) / m
	# elif nn.output == 'softmax':
		# nn.L = -sum(sum(y * log(nn.a[n-1]))) / m
	
	
	
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
		print(size(first_activations))
		# print(first_activations)
		toimage(first_activations.reshape((28,28))).show()
	elif level == 'second':
		second_activations = nn.a[1][0,1:]
		print(size(second_activations))
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
		
		
	