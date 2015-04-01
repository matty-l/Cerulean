"""
	This file contains functions to apply gradients to an mlp
	
	Author: Matthew Levine
	Date: 02/02/2015
"""

from numpy import shape,zeros
from utils.utils import size, addPenalty


def nnapplygrads( nn ):
	""" Updates weights and biases with calculated gradients
	"""
	
	for i in range(nn.n-1):
		if nn.weightPenaltyL2 > 0:
			# zs = zeros((size(nn.W[i])[0],1))
			# apply weight penalty here
			dW = nn.dW[i] + nn.weightPenaltyL2 * addPenalty(nn.W[i][:,1:])
		else:
			dW = nn.dW[i]
			
		# adjust learning rate here
		dW = nn.learningRate * dW
		
		# apply momentum here
		if nn.momentum > 0:
			nn.vW[i] = nn.momentum * nn.vW[i] + dW
			dW = nn.vW[i]
			
		nn.W[i] = nn.W[i] - dW
		
