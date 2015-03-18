"""
	This file contains an immutable token class
	
	Author: Matthew Levine
	Date: 11/28/2014
"""

from operator import itemgetter
# from Scanner.Word import PyWord

class PyToken(tuple):
	""" This class is an immutable scanning token """
	
	__slots__ = []
	
	def __new__(cls,value,rule):
		""" Makes a new token """
		(id,style) = (rule.type,rule.style)
		return tuple.__new__(cls,(str(value),id,style))
		
	value = property(itemgetter(0))
	id = property(itemgetter(1))
	style = property(itemgetter(2))
	
	def __str__(self):
		return self.value.__repr__()
		
		
class EOFToken(PyToken): 
	""" Token for end-of-file """
	def __new__(cls):
		return tuple.__new__(cls,('',-1,''))
	
class ErrorToken(PyToken): 
	""" Token for an error-character """
	def __new__(cls):
		return tuple.__new__(cls,('',-1,''))


