"""
	Profiling
	Author: Matthew Levine
"""

import numpy as np
from math import sqrt
from numpy import array,ones
import time

add = lambda A,B: array([a.tolist() + b.tolist() for a,b in zip(A,B)])

import numpy.random as random

N = 1000**2
M = int(sqrt(N))
print("Making data")
A = random.random((N,1))
print("Made the data")

def timit(A=A,n=10):
	t0 = time.time()
	for i in range(1,n):
		# print(i,'iteration')
		if i % 2 == 0:
			A.reshape((M,M))
		else:
			A.reshape((N,1))
		A[0] += 1
		# add(A,ones((A.shape[0],1)))
	return (time.time() - t0)/n
	
n = int(1e7)
t = timit(n=n)
print(t,'seconds per event for ',n,'events')