"""
	This file contains a monte-carlo tuner of a nueral network
	
	Author: Matthew Levine
	Date: 04/02/2015
"""

from setup import setup
from train import train, Opts
from training.nntest import nntest

from random import random

def bozo_search( architecture, x, y, itermax=-1, filename='tuning.txt' ):
	"""
		Randomly searches the feature space of the neural network for optimal
		hyperparameters
	"""
	
	opts = Opts()
	opts.batchsize = 80 # magic-ish number
	opts.numepochs = 30
	worst = 1
	
	while itermax > 0:
		
		lr  = random() * 10
		mo  = random() * 1
		slr = random()
		wL  = random()
		
		nn = NN( architecture , 
			learningRate = lr,
			momentum = 0.8, 
			scaling_learningRate = slr,
			weightPenaltyl2 = wL )

		train( nn, x, y, opts )
			
		misclass = nntest( nn, x, y )
		if misclass < worst:
				worst = misclass
				file = open(fliename,'w')
				file.write( '\n'.join( ['learning rate',lr,'momentum',mo,
										'scaling lr',slr,'l2 penalty',wL,
										'misclasification',misclass] ) )
				file.close()
		
		itermax -= 1