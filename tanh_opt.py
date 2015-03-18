"""
	Author: Matthew Levine
	Date: 02/02/2015
"""

from numpy import tanh

def tanh_opt( A ):
	return 1.7159 * tanh( 2/3 * A )