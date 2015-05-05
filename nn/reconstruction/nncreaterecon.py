
from reconstruction.nnreconstruct import reconstruct
from feedforward import feedforward 
from scipy.io import savemat, loadmat
from numpy.random import shuffle
from utils.utils import disp
from numpy import zeros


def create_and_save_recon(x=None,y=None,dim=128,batches=20, downsample=0,
		filename='stratified6',epochs=10):
	""" Creates and saves  reconstruction network """

	assert not ((x is None and y is not None) or (x is not None and y is None))

	if x is None and y is None:

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
		
	feedforward( nn_r, x, zeros( (x.shape[0], nn_r.size[-1] ) ) )

	savemat(str(filename),{'v0':nn_r.W[0],'v1':nn_r.W[1],
		'train_x':x,'train_y':y,
		'w0':nn.W[0], 'w1':nn.W[1],
		'i0':nn_i.W[0]})

		
	return nn,x,y