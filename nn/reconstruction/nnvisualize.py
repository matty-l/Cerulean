"""
	This file supports visualizing the layer on a neural network
	
	Author: Matthew Levine
	Date: 03/17/2015
"""
count = 0

import random
from math import sqrt, sin, cos, pi

from scipy.misc import toimage

from feedforward import feedforward as nnff
import numpy as np
	
		
def visualize( nn, x, layers='both', k = 'random', mode='show', use_x = False ):
	""" Visualizes a random layer of the network """
	assert layers in {'both','first','last','neither'}, 'layers must be "first", "last", or "both"'
	assert mode in {'show','save','neither'}, 'mode must be "show", "save", or "neither"'
	
	global count
	count += 1
	
	# if not given, pick a random feature to visualize
	if k != 'singular':
		if k == 'random': i = random.randint(0,x.shape[0])
		else: i = k
			
		dim = sqrt(x[i,:].shape[0])
		if int(dim) == dim:
			dim = int(dim)
		else:
			raise Exception("Can't manage non-square data")
			
		test_x = x[i,:].reshape((dim*dim,1)).transpose()
		
	else:
		dim = sqrt(x.shape[1])
		assert int(dim)==dim,"Can't manage non-square data"
		dim = int(dim)
		test_x = x
	
	# light up the activations of the recon network for visualization
	nnff(nn,test_x,test_x)
	s = ''.join(['0' for i in range(8-len(str(count)))]) + str(count)

	# show the reconstruction layer
	if layers == 'first' or layers == 'both':
		acts = nn.a[2][0]
		
		if mode == 'show':
			toimage(acts.reshape((dim,dim))).show()
		elif mode == 'save':			
			toimage(acts.reshape((dim,dim))).save('../ducky/ducky'+s+'.png')
		
	# if specified, show original input too
	if layers == 'last' or layers == 'both':
		acts = nn.a[0][0][1:]
		if mode == 'show':
			toimage(acts.reshape((dim,dim))).show()
		elif mode == 'save':
			toimage(acts.reshape((dim,dim))).save('../ducky/duck'+s+'.png')
			
	return nn.a[2][0]

		
def testvis(layers='first'):	
	""" Visalizes a layer of a nn activation after ff """

	from scipy.io import loadmat
	from setup import NeuralNetwork as nnsetup

	result = loadmat("goodmatx.mat")
	w1 = result['v1']
	w0 = result['v0']
	x,y = result['train_x'], result['train_y']

	# result = loadmat("ducky.mat")
	# x = result['train_x']
	# y = result['train_y']

	size = [x.shape[1], 1000, y.shape[1]]

	nn = nnsetup([size[0],size[1],size[0]],output='sigm')

	nn.W[0] = w0
	nn.W[1] = w1
	
	for i in range(50):
		visualize( nn, x, k = 3000+i*4, layers=layers, mode='save' )
	
if __name__ == '__main__':
	testrotate()
	