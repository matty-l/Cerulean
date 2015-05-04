"""
	This file contains the functionality to train a neural network
	
	Author: Matthew Levine
	Date: 02/02/2015
"""

from numpy import shape, float as npfloat, zeros, mean
from numpy.random import permutation as randperm, random as rand
from time import time

from feedforward import feedforward

from training.nnbp import nnbp
from training.nnapplygrads import nnapplygrads
from training.nneval import nneval
from utils.nnupdatefigures import nnupdatefigures, nnupdatestatus
from utils.plotter import figure
from utils.utils import disp, verbose


def train( nn, train_x, train_y, opts, val_x=None, val_y=None):
	""" This function trains a neural network
	
		Trains a neural network in place through feed-forward back propogation
		using the number of epochs and batch size indicated in opts.
		The neural network will have updated activations, errors, weights, 
		baises, and loss (the sum squared error for each
		training batch)
	"""
	
	
	nargin = 4 + (val_x is not None) + (val_y is not None)
	
	if verbose:
		assert isfloat(train_x), "train_x must be a float"
		assert nargin == 4 or nargin == 6, "Number of input arguments must be 4 or 6"
		
	loss = Loss()
	
	opts.validation = 0
	if nargin == 6:
		opts.validation = 1
	
	fhandle = []
	if 'plot' in dir(opts) and opts.plot == 1:
		fhandle = figure()
		
	m = train_x.shape[0]
	batchsize = opts.batchsize
	numepochs = opts.numepochs
	
	numbatches = m // batchsize
	
	# this needs to be checked every time, regardless of verbosity. Otherwise,
	# wacky and *very* hard to catch things might happen. Of course, it can
	# still be disabled by turning of debug mode or modifying the C #define
	assert numbatches == m / batchsize, __get_batch_error(m,batchsize)
	
	L = zeros( (numepochs*numbatches+1,1) )
	n = 1
	for i in range(numepochs):
		disp("Starting epoch",i,'of',numepochs)
		nn.update() # observer pattern notificatino
		t0 = time()
		
		kk = randperm(range(m))

		for l in range(numbatches):
			disp("Starting batch ",l,"of",numbatches)
			batch_x = train_x[ kk[l * batchsize : (l+1) * batchsize], : ]
			
			# add noise to input
			if (nn.inputZeroMaskedFraction != 0):
				batch_x *= (rand( batch_x.shape ) > nn.inputZeroMaskedFraction)
				
			batch_y = train_y[ kk[l * batchsize : (l+1) * batchsize], : ]
			
			tdisp = time()
			disp("Feeding forward...",startime=1)
			feedforward( nn, batch_x, batch_y )
			disp("Back propogating...",stoptime=1,startime=1)
			nnbp(nn)
			disp("Gradient Descenting",stoptime=1,startime=1)
			nnapplygrads(nn)
			
			L[n] = nn.L
			
			n = n + 1		
			
		t1 = time() - t0
		
		disp("Calculating loss",startime=1,stoptime=1)
		
		loss = nneval( nn, loss, train_x, train_y, val_x, val_y )
			
		if fhandle != []: nnupdatefigures(nn,fhandle,loss,opts,i)
		nnupdatestatus( i, opts.numepochs )
			
		
		disp("Finished calculating loss.",stoptime=1)
			
		disp('Epoch',i,'/',str(opts.numepochs)+' took',t1,'seconds.',
			'Training Error (mbmse):',mean(L[(n-numbatches):n]))
			
		timing = loss.timing
		timing.append(t1)
		disp("Projected time: ", sum(timing) / len(timing) * (opts.numepochs - i), " seconds")
			
		nn.learningRate = (nn.learningRate * nn.scaling_learningRate) ** nn.power_learningRate

# probably a better way to do this, but only in debug mode so who cares
isfloat = lambda l : (all([all(tx) for tx in l.astype(npfloat) == l]))
		
def __get_batch_error(m,b):
	""" Returns an error message raised by assertion in the main training
		loop setup. Used only internally
	"""
	g = '?'
	for i in range(1,500):
		if m%(b+i) == 0:
			g = str(b+i)
			break
	h = '0'
	for i in range(8,b):
		if m%(i) == 0:
			h = str(i)
			break
			
	err = m%b
	m,b,err = str(m),str(b),str(err)
	return ' '.join(["The number of batches must be integral;",b,"divides",m,
		"with a remainder of ",err+'.','Try',g,'or',h,'instead'])
		
			
class Loss:
	""" Contains loss information """
	def __init__( self ):
		""" Constructs an empty loss object """
		
		class Session: pass
		
		self.train = Session()
		self.val = Session()

		self.train.e = []
		self.train.e_frac = []
		self.timing = []
		self.val.e = []
		self.val.e_frac = []

		
class Opts: 
	""" Contains options for training """
	def __init__( self ):
		self.batchsize = 0
		self.numepochs = 0
		self.plot = 0
		
def train_net_from_data( filename='ducky.mat', batches=80, innerdim=1000 ):
	""" Trains a network from data """
	
	from scipy.io import loadmat # bad place for import statements
	from scipy.io import savemat
	from setup import NeuralNetwork as nnsetup

	result = loadmat(filename)

	x = result['train_x'].astype(float) / 255
	y = result['train_y'].astype(float)
		
	size = [x.shape[1] , innerdim, 3, y.shape[1]]
	
	opts = Opts()
	opts.batchsize = batches
	opts.numepochs = 30 #numepochs
	opts.plot = 1
	
	nn = nnsetup( size, output='softmax' )
	train( nn, x, y, opts )
	feedforward(nn,x,y)

	savemat('nn/stratified',{'w0':nn.W[0],'w1':nn.W[1],
		'train_x':x,'train_y':y})

		
	return nn,x,y



if __name__ == 'Environment.Terminal' or __name__ == '__main__':

	opts = Opts()
	opts.batchsize = 50
	opts.numepochs = 20
	opts.plot = 1
	
	sample_size = 100
	from setup import NeuralNetwork as nnsetup
	from numpy import array, float
	from random import random
	from scipy.io import loadmat
	
	print("Loading data...")
	try:
		result = loadmat('mnist_uint8.mat')
	except IOError:
		result = loadmat('nn/mnist_uint8.mat')
	
	nn = nnsetup([784,100,10])
	x = result['train_x'].astype(float) / 255
	y = result['train_y'].astype(float)
	
	# downsample for testing
	x = x[:sample_size,:]
	y = y[:sample_size,:]
	
	print("training data...")
	train( nn, x, y, opts )
	print('done training')
		
	from utils.plotter import drawnow
	#drawnow(True)



