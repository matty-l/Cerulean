add_path('nn')

from nn.utils.nnvisualize import visualize
from nn.invert import load_recon
from scipy.io import loadmat

from math import sqrt
from nn.utils.utils import udim

import sys



def build_sequence( Rnn, Ann, x, y , startindex =0, tolerance = 100 ):
	""" Builds and saves a sequence of images from a reconstruction matrix,
	     a trained matrix, and the original x/y datasets

	     Optional Arguments:
	     	startindex : the index in x to start shifting through
		tolerance : the maximum number of images to shift through

	     Note that a negative tolerance will loop forever, on purpose, writing out more images
	     in the sequence.
	"""

	dim = udim(x[1,:])
	try:
		x = x[ startindex , : ]
	except IndexError: # an ounce of cure is worth two preventions in the bush... or something
		raise Exception( "Starting index cannot be bigger than dim(x)")

	while (tolreance != 0):
		x = x.reshape((dim*dim,1)).transpose()
		x = visualize(Rnn,x,mode='save',layers='first', k = 'singular',reject=True)
		
		tolerance -= 1
	
	
def test_sequence():
	Rnn,Ann,(x,y) = load_recon('goodmatx')
	build_sequence(Rnn,Ann,x,y)
