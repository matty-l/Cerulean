"""
	This file contains the functionality to train a neural network
	
	Author: Matthew Levine
	Date: 02/02/2015
"""

from numpy import shape, float as npfloat, zeros, mean
from numpy.random import permutation as randperm, random as rand
from time import time

from nnff import nnff

from training.nnbp import nnbp
from training.nnapplygrads import nnapplygrads
from training.nneval import nneval

from utils.nnupdatefigures import nnupdatefigures
from utils.plotter import figure
from utils.utils import size

isfloat = lambda l : (all([all(tx) for tx in l.astype(npfloat) == l]))

__verbose__ = 0

def disp(*words):
	if __verbose__: print(words)


def nntrain( nn, train_x, train_y, opts, val_x=None, val_y=None):
	""" This function trains a neural network
	
		Trains a neural network in place through feed-forward back propogation
		using the number of epochs and batch size indicated in opts.
		The neural network will have updated activations, errors, weights, 
		baises, and loss (the sum squared error for each
		training batch)
	"""
	
	
	nargin = 4 + (val_x is not None) + (val_y is not None)
	
	assert isfloat(train_x), "train_x must be a float"
	assert nargin == 4 or nargin == 6, "Number of input arguments must be 4 or 6"
		
	loss = Loss()
	loss.train.e = []
	loss.train.e_frac = []
	loss.val.e = []
	loss.val.e_frac = []
	
	opts.validation = 0
	if nargin == 6:
		opts.validation = 1
	
	fhandle = []
	if 'plot' in dir(opts) and opts.plot == 1:
		fhandle = figure()
		
	m = size(train_x)[0]
	batchsize = opts.batchsize
	numepochs = opts.numepochs
	
	numbatches = m // batchsize
	
	assert numbatches == m / batchsize, 'numbatches must be an integer'
	
	L = zeros( (numepochs*numbatches+1,1) )
	n = 1
	for i in range(numepochs):
		t0 = time()
		
		kk = randperm(range(m))

		for l in range(numbatches):
			batch_x = train_x[ kk[l * batchsize : (l+1) * batchsize], : ]
			
			# add noise to input
			if (nn.inputZeroMaskedFraction != 0):
				batch_x = batch_x * (rand( size(batch_x) ) > nn.inputZeroMaskedFraction)
				
			batch_y = train_y[ kk[l * batchsize : (l+1) * batchsize], : ]
			
			nnff( nn, batch_x, batch_y )
			nnbp(nn)
			nnapplygrads(nn)
			
			L[n] = nn.L
			
			n = n + 1
	
		t1 = time() - t0
		if opts.validation == 1:
			loss = nneval( nn, loss, train_x, train_y, val_x, val_y )
			str_perf = '; Full-batch train mse = %f, val mse = %f' % (loss.train.e[-1], loss.val.e[-1]) 
		else:
			loss = nneval(nn,loss,train_x,train_y)
			str_perf = '; Full-batch train err = %f' % loss.train.e[-1]
			
		if fhandle != []:
			nnupdatefigures(nn,fhandle,loss,opts,i)
			
		disp('epoch',i,'/',str(opts.numepochs)+'. Took',t1,'seconds.',
			'Mini-batch mean squared error on training set is',
			mean(L[(n-numbatches):n]), str_perf)
			
		nn.learningRate = nn.learningRate * nn.scaling_learningRate
		
			
class Loss:
	""" Contains loss information """
	def __init__( self ):
		""" Constructs an empty loss object """
		
		class Session: pass
		
		self.train = Session()
		self.val = Session()
		
class Opts: 
	""" Contains options for training """
	def __init__( self ):
		self.batchsize = 0
		self.numepochs = 0
		self.plot = 0


if __name__ == 'Terminal' or __name__ == '__main__':
	opts = Opts()
	opts.batchsize = 50
	opts.numepochs = 10
	opts.plot = 1
	
	sample_size = 1000
	
	from nnsetup import nnsetup
	from numpy import array, float
	from random import random
	from scipy.io import loadmat
	
	print("Loading data...")
	result = loadmat('mnist_uint8.mat')
	
	nn = nnsetup([784,100,10])
	x = result['train_x'].astype(float) / 255
	y = result['train_y'].astype(float)
	
	# downsample for testing
	x = x[:sample_size,:]
	y = y[:sample_size,:]
	
	print("training data...")
	nntrain( nn, x, y, opts )
		
	from utils.plotter import drawnow
	drawnow(True)


