"""
	This file contains the class that inverts a neurnal network function
	
	Author: Matthew Levine
	Date: 03/15/2015
"""

from setup import NeuralNetwork as nnsetup
from train import train as nntrain,Opts
from feedforward import feedforward as nnff

from numpy import array, float, shape, zeros
from numpy import roll as nproll
from numpy.random import shuffle

from utils.utils import disp, get_command, get_flag_value
from utils.view_mats import view_mats
import reconstruction.nnvisualize
import reconstruction.nnbuild_sequence 

from scipy.io import loadmat


def reconstruct( x, y, batchsize=50, numepochs=10, architecture=[784,1000,10]):
	""" Returns an inverted form of the network.

		This technique was developed by Carlos Vallespi and Carl Welington's 
		team at NREC at Carnegie mellon in the summer of 2014. They are awesome
		people.
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
	nn = nnsetup( size, output='softmax' )
	disp("Training initial network")
	nntrain( nn, x, y, opts )
	nnff(nn,x,y)
	
	# train the inversion network
	disp("Training the inversion network")
	size_n = [size[1], size[0]]
	nn_i = nnsetup( size_n, output='sigm' )
	y_n = nn.a[0][:,1:]
	x_n = nn.a[1][:,1:]
	
	# shift x
	# x_n = nproll( x_n, 1, 0 )
	
	nntrain( nn_i, x_n, y_n, opts )	
		
	disp("Compiling reconstruction network")
	# compile into reconstruction network
	nn_r = nnsetup( [size[0],size[1],size[0]], output='sigm' )
	nn_r.W[0] = nn.W[0]
	nn_r.W[1] = nn_i.W[0]
		
	return nn_r, nn, nn_i


def load_recon( filename, innerdim = 1000 ):
	""" Loads and returns a reconstruction network and the original input network
		from the indicated file . Also returns x and y
	"""
	result = loadmat(filename if filename.endswith('.mat') else filename+'.mat')
	
	# Make the recon net
	v1,v0 = result['v1'], result['v0']

	x,y = result['train_x'], result['train_y']

	size = [x.shape[1], innerdim, y.shape[1]]

	nn_r = nnsetup([size[0],size[1],size[0]],output='sigm')

	nn_r.W[0] = v0
	nn_r.W[1] = v1
	
	w1,w0 = result['w1'], result['w0']
	
	nn = nnsetup([size[0],size[1],size[2]],output='softmax') # assume softmax
	nn.W[0] = w0
	nn.W[1] = w1
	
	return nn_r, nn, (x,y)

	
def create_and_save_recon(x=None,y=None,dim=128,batches=20, downsample=0,
		filename='stratified6',epochs=10):
	""" Creates and saves  reconstruction network """

	assert not ((x is None and y is not None) or (x is not None and y is None))

	if x is None and y is None:
		from scipy.io import loadmat

		# result = loadmat('mnist_uint8.mat')
		disp("Loading data...")
		result = loadmat('C:/Users/Dev/Desktop/ducky2.mat')
		disp("Data loaded")

		disp("Processing data...")
		x = result['train_x'].astype(float) / 255
		y = result['train_y'].astype(float)
		
		shuffle(x)
		shuffle(y)
		disp("Data processed")
		
		if downsample:
			sample_size = 80
			
			# downsample for testing
			x = x[:sample_size,:]
			y = y[:sample_size,:]
		
	nn_r,nn,nn_i = reconstruct( x, y, batchsize=batches, 
		architecture=[x.shape[1] , 1000, y.shape[1]], numepochs=epochs )
		
	nnff( nn_r, x, zeros( (x.shape[0], nn_r.size[-1] ) ) )

	from scipy.io import savemat
	savemat(str(filename),{'v0':nn_r.W[0],'v1':nn_r.W[1],
		'train_x':x,'train_y':y,
		'w0':nn.W[0], 'w1':nn.W[1],
		'i0':nn_i.W[0]})

		
	return nn,x,y
	
def test_sequence_build(filename,startindex):
	""" Tests the ability to build sequences """
	reconstruction.nnbuild_sequence.test_sequence(filename,startindex=startindex)
	
def main():
	import sys
	
	command = get_command("Flags:\n--make\n  (--batches [%d])\n  (--filename [%s])\n--show\n--demo")
	if command is None:
		disp("Terminating because don't recognize command")
		exit(3)
		
	filename = get_flag_value('filename',str,'stratified')
	numbatches = get_flag_value('batches',int,50)
	start = get_flag_value('start',int,0)
	downsample = get_flag_value('downsample',int,0)
	epochs = get_flag_value('epochs',int,10)
	
	if any((flag is None for flag in (filename,numbatches,start))):
		disp("Terminating due to misformatted flag")
		exit(1)
	
		
	if command == '--make':			
		create_and_save_recon(batches=numbatches,filename=filename,
			downsample=downsample,epochs=epochs)
	elif command == '--show':
		test_sequence_build(filename,start)
	elif command == '--demo':
		nnvis.testvis()
	elif command == '--view_mats':
		disp(view_mats())
	else:
		disp("Uknown command ",command)

	
if __name__ == '__main__':
	main()
	# test_sequence_build()
	# create_and_save_recon(downsample=0)
	
	# from reconstruction.nnvisualize import testvis as testvis
	# testvis()
