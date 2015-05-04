from reconstruction.nnvisualize import visualize
from invert import load_recon
from scipy.io import loadmat

from math import sqrt
from utils.utils import udim, disp
from training.nnpredict import nnpredict 

import sys



def build_sequence( Rnn, Ann, x, y , startindex = 1800, tolerance = 1000 ):
	""" Builds and saves a sequence of images from a reconstruction matrix,
	     a trained matrix, and the original x/y datasets

	     Optional Arguments:
	     	startindex : the index in x to start shifting through
			tolerance : the maximum number of images to shift through

	     Note that a negative tolerance will loop forever, on purpose, writing out more images
	     in the sequence.
	"""
	dim = udim(x[1,:])
	x0 = x
	try:
		x = x[ startindex , : ]
	except IndexError: # an ounce of cure is worth two preventions in the bush... or something
		raise Exception( "Starting index cannot be bigger than dim(x) ["+str(x.shape)+"]")

	x = x.reshape((dim*dim,1)).transpose()
	class0 = nnpredict(Ann,x)
		
	i = 0
	while (tolerance != 0):
		x = x.reshape((dim*dim,1)).transpose()
		
		# only save the image if it's of the right class
		classf = nnpredict( Ann, x )

		mode = 'show' if classf == class0 else 'neither'
		
		x = visualize(Rnn, x, mode=mode, layers='first', k='singular')
		
		# for testing
		x = x0[ startindex+i , : ]
		
		tolerance -= 1
		if tolerance % 10 == 0 and tolerance+i != 0:
			disp("At",(1-tolerance/(tolerance+i))*100,'% of tolerance')
		i += 1
	
	
def test_sequence(filename='stratified5',startindex=1000):
	Rnn,Ann,(x,y) = load_recon(filename)
	build_sequence(Rnn,Ann,x,y,startindex=startindex)
