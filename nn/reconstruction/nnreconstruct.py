"""
	Reconstucts an input using neural networks
	
	Author: Matthew Levine
	Date: 05/04/2015

"""

from scipy.io import savemat
from numpy import roll as nproll
from utils.utils import disp

from train import train as nntrain,Opts
from feedforward import feedforward
from setup import NeuralNetwork 


def reconstruct( x, y, batchsize=50, numepochs=10, architecture=[784,1000,10]):
	""" Returns an inverted form of the network.

		This technique was developed by Carlos Vallespi and Carl Welington's 
		team at NREC at Carnegie mellon in the summer of 2014. They are awesome
		people.
		
		Returns the reconstruction network, the initial network, and the
		inner network
		
		Arguments:
			x,y (required): the input and output
			batchsize: number of batches to use during training
			numepochs: number of epochs to use during training
			architcture: the architecture of the inital network
			
		This function returns a network that maps to an inner layer and then
		maps back to the input space. The map is rolled, and expects the given
		feature as input
	"""
	
	size = architecture
	assert len(size) == 3,  "Only able to do 3-layer reconstructions right now"
	
	# set up options
	opts = Opts()
	opts.batchsize = batchsize
	opts.numepochs = numepochs
	opts.plot = 1
		
	disp("Setting up initial network")
	# train the original network
	nn = NeuralNetwork( size, output='softmax' )
	disp("Training initial network")
	nntrain( nn, x, y, opts )
	feedforward(nn,x,y)
	
	# train the inversion network
	disp("Training the inversion network")
	size_n = [size[1], size[0]]
	nn_i = NeuralNetwork( size_n, output='sigm' )
	y_n = nn.a[0][:,1:]
	x_n = nn.a[1][:,1:]
	
	# shift x
	# x_n = nproll( x_n, 1, 0 )
	
	nntrain( nn_i, x_n, y_n, opts )	
		
	disp("Compiling reconstruction network")
	# compile into reconstruction network
	nn_r = NeuralNetwork( [size[0],size[1],size[0]], output='sigm' )
	nn_r.W[0] = nn.W[0]
	nn_r.W[1] = nn_i.W[0]
		
	return nn_r, nn, nn_i




	