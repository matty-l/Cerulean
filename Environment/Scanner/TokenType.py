"""
	This file contains enumerated token types
	
	Author: Matthew Levine
	Date: 11/28/2014
"""


class PyTokenType:
	""" Enumerated token types """

	# white space
	new_line = 1	
	comment = 2
	whitespace = 3

	# errors
	EOF = -1
	LEX_ERROR = -3
	
	# literals
	number = 10
	literal = 11
	keyword = 14
	string = 15

	# symbols
	operator = 20
	delimeter = 21
	
	def lookup( token ):
		return {1:'new_line',2:'comment',3:'whitespace',-1:'EOF',-3:'LEX_ERROR',
				10:'number',11:'literal',14:'keyword',15:'string',
				20:'operator',21:'delimeter'}[token.id]