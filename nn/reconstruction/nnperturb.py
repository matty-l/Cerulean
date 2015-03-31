"""
	This file contains functions that perturb an intup to find another 
	valid input
	
	Author: Matthew Levine
	Date: 03/17/2015
"""

import numpy as np
from utils import Overrides, udim
import random

from nnff import nnff
from nnpredict import nnpredict

__verbose__ = 1

def display(*args):
	if __verbose__:print(*args)

class PerturbanceModule:
	""" This class fascilitates purturbances on an input """
	
	def __init__( self, E0, label, index, Ann, Rnn, function = 'single' ):
		"""
			Takes an original input (defined to be standard basis) with its
			label and index, the original X->Y network, and the recon network.
			
			Takes optionally the name of a perturbance function to be used.
		"""
		# validate input
		legit = {'single':SingleJitterPerturbance}
		if function not in legit:
			raise Exception("Perturbance function must be in "+str(list(legit.keys())))
			
		self.function = legit[function]()
		self.dim = udim(E0.transpose())
	
		self.e0 = E0
		self.ei = [self.e0] # holds the future inputs in X
		
		self.A = Ann # the original network
		self.R = Rnn #the recon network
		self.label = label.argmax()
		self.index = index

		self.tao = self.getReconError( E0 ) # tolerance on recon
		
	def getReconError( self, Ei ):
		""" Returns the reconstruction error on an element """
		# get recon
		x = Ei.reshape((self.dim*self.dim,1)).transpose() # this call might be extraneous
		
		nnff( self.R, x, x )
		
		recon = self.R.a[2]
		
		# get difference image
		Ep = x - recon 
		Ep *= Ep
				
		# normalize by energy?
				
		return sum(Ep.transpose())[0] 
		

		
	def perturb( self, n = 1 ):
		""" Applies a perturbance function until it finds a viable continuant, 
			then internalizes it
		"""
		ej = self.function.jitter(self.ei[-1])
				
		while not self.validate(ej):
			ej = self.function.jitter(self.ei[-1].reshape((1,self.dim*self.dim,)))
			
		self.ei.append(ej)
		display("Found one,",n-1,'left')

		if n > 1:
			self.perturb(n-1)
		return ej
		
	
	def validate( self, Ei ):
		""" Returns true if and only if Ei is a valid transform on Ei within	
			X
		"""
		x = Ei.reshape((1,self.dim*self.dim))
		
		# validate with A (not sure this is neccessary)
		label = nnpredict(self.A,x)[0]
		if label != self.label:
			return False
			
		# validate with R
		return self.getReconError(x) <= self.tao
			
			
		
	def binary_of( self, input, thresh = .5 ):
		""" Returns the binary form of the input """
		e0 = input.copy()
		for i,row in enumerate(e0):
			e0[i] = 1 * (row > .5)
		return e0
		
		
from abc import ABCMeta, abstractmethod

class PerturbanceFunction(object):
	""" Abstract base-class for perturbance functions """
	__metaclass__ = ABCMeta
	
	@abstractmethod
	def jitter( self, other ): pass
	
class SingleJitterPerturbance(PerturbanceFunction):

	@Overrides(PerturbanceFunction)
	def jitter(self, other):
		other = other.copy()
		i,j = (random.randint(0,other.shape[k]-1) for k in range(2))
		while other[i,j] == 0:
			i,j = (random.randint(0,other.shape[k]-1) for k in range(2))
		other[i,j] = 1 - other[i,j]
		return other
		
if __name__ == '__main__':
	from nnsetup import nnsetup
	from nninvert import load_recon
	
	print("Loading data")
	Rnn,Ann,(x,y) = load_recon( 'goodmatx' )
	print("Data loaded")
	
	k = 3000
	E0 	  = x[k,:]
	dim = udim(E0)
	E0 = E0.reshape((dim*dim,1)).transpose()
	label = y[k,:]

	pTB = PerturbanceModule(E0, label, k, Ann, Rnn)
	print("Perturbing...")
	pTB.perturb(100)
	print("Done perturbing")
	
	print("Saving data")
	from scipy.io import savemat
	savemat('data/new.mat',{'e'+str(i) : el for i,el in enumerate(pTB.ei)})
	print("Done")