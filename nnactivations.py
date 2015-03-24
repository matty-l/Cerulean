"""
	This file contains activation functions
	
	Author: Matthew Levine
	Date: 03/23/2015
"""

from abc import ABCMeta, abstractmethod
from utils import Overrides
from numpy import tanh, exp


class ActivationFunctionImpl(object):

	__metaclass__ = ABCMeta
	
	@abstractmethod
	def feedforward( self, layer, weights ): pass
	
	@staticmethod
	def factory(name):
		amap =  {'sigm':SigmActivation,'tanh_opt':TanhOptActivation}
		assert name in amap, 'Cannot produce unkown function'+str(name)
		return amap[name]()
	
	
class SigmActivation(ActivationFunctionImpl):
	
	@Overrides(ActivationFunctionImpl)
	def feedforward( self, layer, weights ):
		sigm = lambda P : 1 / (1+exp(-P))
		return sigm(layer.dot(weights.transpose()))
		
class TanhOptActivation(ActivationFunctionImpl):
	
	@Overrides(ActivationFunctionImpl)
	def feedforward(self, layer, weights):
		tanh_opt = lambda A : 1.7159 * tanh( 2/3 * A )
		return tanh_opt(layer.dot(weights.transpose()))