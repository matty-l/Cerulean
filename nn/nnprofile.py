"""
	This file profiles various functions in the nn libary
	
	Author: Matthew Levine
	Date: 03/24/2015
"""

from setup import setup
from train import train, Opts

from numpy import array, float
from random import random
from scipy.io import loadmat

import profile


def nnprofile( stage_name ):
	""" Profiles the function of the given name """
	function_names = {'profile_nntrain'}
	assert stage_name in function_names, 'Uknown stage name '+str(stage_name)
	profile.run(stage_name+'()')

def profile_nntrain( ):
	""" Profiles the setup and training of a neural network """
	nn = setup([784, 100, 10])
	
	opts = Opts()
	opts.batchsize = 50
	opts.numepochs = 10
	opts.plot = 1
	
	sample_size = 1000
	
	
	print("Loading data...")
	result = loadmat('mnist_uint8.mat')
	
	nn = setup([784,100,10])
	x = result['train_x'].astype(float) / 255
	y = result['train_y'].astype(float)
	
	# downsample for testing
	x = x[:sample_size,:]
	y = y[:sample_size,:]
	
	print("training data...")
	train( nn, x, y, opts )

if __name__ == '__main__':
	nnprofile('profile_nntrain')