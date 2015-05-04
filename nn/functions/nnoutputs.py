"""
	This file contains output functions
	
	Date: 03/18/2015
"""

from abc import ABCMeta, abstractmethod
from utils.utils import Overrides
from numpy import sum, log
from numpy import exp, max, sum
from linalg.CeLinalg import dot as cdot


class OutputFunction(object):
	__metaclass__ = ABCMeta
	
	@abstractmethod
	def back_propogate(self, error, layer ): pass
	
	@abstractmethod
	def evaluate_loss( self, error, m, layer, y ): pass
	
	@abstractmethod
	def feedforward( self, layer, weights): pass
	
	@staticmethod
	def factory( classname ):
		mapf = {'softmax':SoftmaxOutput,'sigm':SigmoidOutput}
		assert classname in mapf, 'Cannot produce unknown function'+str(classname)
		return mapf[classname]()
			
	
class SoftmaxOutput(OutputFunction):
	
	@Overrides(OutputFunction)
	def back_propogate(self, error, layer=None ):
		return -error
		
	@Overrides(OutputFunction)
	def evaluate_loss( self, error, m, layer, y):
		return -sum(sum(y * log(layer))) / m
		
	@Overrides(OutputFunction)
	def feedforward( self, layer, weights ):

		def softmax(x):
			max_x = max(x,1)
			max_x.shape = (max_x.shape[0],1)
			x = exp( x - max_x )
			sum_x = sum(x,1)
			sum_x.shape = (sum_x.shape[0],1)
			x = x / sum_x

			return x
			
		return softmax(cdot(layer,weights.transpose()))
		
		
class SigmoidOutput(OutputFunction):
	
	@Overrides(OutputFunction)
	def back_propogate(self, error, layer):
		return - error * (layer * (1-layer))
		
	@Overrides(OutputFunction)
	def evaluate_loss(self, error, m, layer, y ):
		return 1/2 * sum(sum(error * error)) / m
		
	@Overrides(OutputFunction)
	def feedforward( self, layer, weights ):
		sigm = lambda P : 1 / (1+exp(-P))
		return sigm(cdot(layer,weights.transpose()))