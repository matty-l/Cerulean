"""
	This file contains the class that inverts a neurnal network function
	
	Author: Matthew Levine
	Date: 03/15/2015
"""

from nnsetup import nnsetup
from nntrain import nntrain,Opts
from feedforward import feedforward as nnff

from numpy import array, float, shape, zeros
from numpy import roll as nproll

from utils.utils import size

from scipy.io import loadmat

__verbose__  = 1

def disp(words):
	global __verbose__
	if __verbose__:print(words)


def reconstruct( x, y, batchsize=50, numepochs=10, architecture=[784,100,10]):
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
		
	# train the original network
	# print("Training first network...")
	nn = nnsetup( size, output='softmax' )
	nntrain( nn, x, y, opts )
	nnff(nn,x,y)
	
	# train the inversion network
	size_n = [size[1], size[0]]
	nn_r = nnsetup( size_n, output='sigm' )
	y_n = nn.a[0][:,1:]
	x_n = nn.a[1][:,1:]
	
	# shift y
	y_n = nproll( y_n, 1, 0 )
	
	nntrain( nn_r, x_n, y_n, opts )	
		
	# compile into reconstruction network
	nn_f = nnsetup( [size[0],size[1],size[0]], output='sigm' )
	# print(nn_f.W[0].shape,nn_f.W[1].shape
	nn_f.W[0] = nn.W[0]
	nn_f.W[1] = nn_r.W[0]
		
	# print(nn_f.W[0].shape,nn_f.W[1].shape)
	return nn_f, nn


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

	
def test_recon(x=None,y=None,dim=128,batches=80, downsample=False):

	assert not ((x is None and y is not None) or (x is not None and y is None))

	if x is None and y is None:
		from scipy.io import loadmat
		print("Loading data...")
		# result = loadmat('mnist_uint8.mat')
		result = loadmat('ducky.mat')


		x = result['train_x'].astype(float) / 255
		y = result['train_y'].astype(float)
		
		if downsample:
			sample_size = 80
			
			# downsample for testing
			x = x[:sample_size,:]
			y = y[:sample_size,:]
		
	nn,nn_0 = reconstruct( x, y, batchsize=batches, architecture=[x.shape[1] , 100, y.shape[1]] )
		
	nnff( nn, x, zeros( (size(x)[0], nn.size[-1] ) ) )
		
	# for i in range(1,11):
		# visualize(nn, dim, x )

	from scipy.io import savemat
	savemat('goodmatx',{'v0':nn.W[0],'v1':nn.W[1],
		'train_x':x,'train_y':y,
		'w0':nn_0.W[0], 'w1':nn_0.W[1]})

		
	return nn,x,y
	

	
if __name__ == '__main__':
	test_recon()
