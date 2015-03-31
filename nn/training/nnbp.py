"""
	This file contains back-propogation functions
	
	Author: Matthew Levine
	Date: 02/02/2015
"""

from numpy import tile, shape, zeros, pi, array, ones

def repmat( a, m, n ):
	return tile(a,(m,n))
	
size = lambda x:shape(x)
add = lambda A,B: array([a.tolist() + b.tolist() for a,b in zip(A,B)])


def nnbp(nn):
	""" Performs backpropogation
		
		Updates the weights of the network in place
	"""
	
	n = nn.n

	d = {}
	if not 'dW' in dir(nn): nn.dW = {}
	
	d[n-1] = nn.output_function.back_propogate( nn.e, nn.a[n-1] )
	# if nn.output == 'sigm':
		# d[n-1] = - nn.e * (nn.a[n-1] * (1-nn.a[n-1]))
	# elif nn.output == 'softmax':
		# d[n-1] = -nn.e
		
	for i in range( n-2, 0, -1 ):
		# derivative of activation function
		if nn.activation_function == 'sigm':
			d_act = nn.a[i] * (1-nn.a[i])
		elif nn.activation_function == 'tanh_opt':
			d_act = 1.7159 * 2/3 * (1 - 1/(1.759)**2 * nn.a[i]*nn.a[i])
						
		# backpropogate first derivates
		if i+2 == n: # in this case in d[n] ther is not the bias term to be removed
			d[i] = (d[i+1].dot(nn.W[i]) ) * d_act
		else: # in this case in d[i] the bias term has to be removed
			d[i] = (d[i+1][:,1:].dot(nn.W[i])) * d_act
			
		if nn.dropoutFraction > 0:
			d[i] = d[i] * add( ones( (size(d[i])[0],1) ), nn.dropOutMask[i] )
			
	for i in range(n-1):
		if i + 2 == n:
			nn.dW[i] = (d[i+1].transpose().dot(nn.a[i])) / size(d[i+1][0])
		else:
			nn.dW[i] = (d[i+1][:,1:].transpose().dot(nn.a[i])) / size(d[i+1])[0]
				
