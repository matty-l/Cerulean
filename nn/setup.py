"""
	This file contains the root constructor for a basic neural network
	
	Author: Matthew Levine
	Date: 02/02/2015
"""

from numpy import sqrt, zeros, shape
from numpy.random import random as rand

from functions.nnoutputs import OutputFunction
from functions.nnactivations import ActivationFunctionImpl

class NeuralNetwork:
	""" This class is emulates a multi-layer perceptron """
	
	observables = [] # note the possibilit of a memory leak
	
	def __init__( self, architecture, freeze_init = False, **kwargs ):
		""" Constructs a new multilayer perceptron """
		self.size = architecture
		self.n = len(self.size)
		
		self.activation_function = 'tanh_opt'
		self.learningRate = 2
		self.momentum = 0.8
		self.scaling_learningRate = 1
		self.power_learningRate = 1
		self.weightPenaltyL2 = 0

		self.inputZeroMaskedFraction = 0
		self.dropoutFraction = .05
		self.testing = 0
		self.output = 'softmax'
				
		for key, val in kwargs.items():
			setattr(self,key,val)
			
		self.output_function = OutputFunction.factory(self.output)
		self.activation_function_impl = ActivationFunctionImpl.factory(self.activation_function)
		
		self.W = {}
		self.vW = {}
		self.p = {}
		self.a = {} # move me?
		self.dropOutMask = {} # move me
		if freeze_init:
			return
			
		# see https://web.stanford.edu/class/ee373b/nninitialization.pdf for maybe
		# a better weight function
		for i in range(1,self.n):
			# weights and weight momentum
			self.W[i-1] = (rand((self.size[i],self.size[i-1]+1)) - 0.5) * 2 * 4 * sqrt(6 / (self.size[i] + self.size[i-1]))
			self.vW[i-1] = zeros((self.W[i-1].shape))
			
			# average activations (for use with sparsity)
			self.p[i] = zeros((1,self.size[i]))
	
	def properties( self ):
		return [ (str(element),self.__dict__[str(element)] if str(element) in self.__dict__ else "?") for element in dir(self) ]

	def copy( self ):
		""" Returns a copy of the neural network """
		nn = NeuralNetwork(self.size,freeze_init=1)
		nn.W = {key:val.copy() for key,val in self.W.items()}
		nn.vW = {key:val.copy() for key,val in self.vW.items()}
		nn.a = {key:val.copy() for key,val in self.a.items()}
		nn.p = {key:val.copy() for key,val in self.p.items()}
		return nn
		
	@staticmethod
	def watch( function ):
		""" Adds an observable to the network """
		NeuralNetwork.observables.append(function)
		
	def update( self ):
		""" Fires all observables """
		[observable() for observable in self.observables]
				
	
if __name__ == '__main__':
	# test code
	nn = NeuralNetwork([784,100,10],output='sigm')
	print(nn.output)