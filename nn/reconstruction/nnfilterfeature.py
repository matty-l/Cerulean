"""
	This file contains code to filter from a set of activations a particular
	feature
	
	Author: Matthew Levine
	Date: 05/04/2015
"""

def filter_feature( x, y, feature ):
	""" Returns the elements of x that correspond to feature """
	return x[ y == feature, : ]
	
if __name__ == '__main__':
	from scipy.io import loadmat
	r = loadmat('ducky.mat'
