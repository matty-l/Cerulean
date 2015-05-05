"""
	Loads a reconstruction network from a file 
	
	Author: Matthew Levine
	Date: 05/04/2015
"""

from scipy.io import loadmat
from setup import NeuralNetwork 

def load_recon( filename, innerdim = 1000 ):
	""" Loads and returns a reconstruction network and the original input network
		from the indicated file . Also returns x and y
	"""
	result = loadmat(filename if filename.endswith('.mat') else filename+'.mat')
	
	# Make the recon net
	v1,v0 = result['v1'], result['v0']

	x,y = result['train_x'], result['train_y']

	size = [x.shape[1], innerdim, y.shape[1]]

	nn_r = NeuralNetwork([size[0],size[1],size[0]],output='sigm')

	nn_r.W[0] = v0
	nn_r.W[1] = v1
	
	w1,w0 = result['w1'], result['w0']
	
	nn = NeuralNetwork([size[0],size[1],size[2]],output='softmax') # assume softmax
	nn.W[0] = w0
	nn.W[1] = w1
	
	return nn_r, nn, (x,y)