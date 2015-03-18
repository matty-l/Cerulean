"""
	This class is a wrapping class for words.
	
	Author: Matthew Levine
	Date: 11/30/2014
"""
from operator import itemgetter

class PyWord(tuple):
	""" This semi-mutable class wraps a word. The value of a word
		is immutable. The syllable-count, etc., can be dynamically
		updated via the word definition.
		
		All definition values should be immutable, or references will be
		copied when PyWord's are created from one another (e.g., the "lower"
		method)
	"""
	__slots__ = []
	
	def __new__(cls,value,definition=None):
		""" Makes a new word. All values are converted to strings """
		return tuple.__new__(cls,(str(value),definition if definition is not None else {}))
		
	value = property(itemgetter(0))
	definition = property(itemgetter(1))
	
	def config( self, *args, **kwargs ):
		""" If an argument is provided, returns that value in the definition.
			If multiple arguments are provided, returns a tuple of those
			values in the definition. If keyword arguments are provided,
			sets the value in the dictionary corresponding to the provided
			key with the provided value.
			
			Raises an exception if a key is solicited which is not defined
		"""
			
		if len(kwargs.items()) > 0:
			for key,value in kwargs.items():
				self.definition[key] = value
		if len(args) == 1:
			return self.definition[args[0]]
		if len(args) > 1:
			return (self.definition[arg] for arg in args)
		
	def __repr__(self):
		""" Returns the value of the word """
		return self.value
				
	def lower(self):
		""" Returns a lower case version of this word """
		return PyWord(self.value.lower(),self.definition)

	def upper(self):
		""" Returns a upper case version of this word """
		return PyWord(self.value.upper(),self.definition)
		
	def __add__( self, other ):
		""" Adds the value of this word to the other object's value, or to the
			other object if that fails"""		
		try: return self.value + other.value
		except AttributeError: return self.value + other
	
	def __radd__( self, other ):
		""" Adds the value of this word to the other object's value, or to the
			other object if that fails
		"""		
		try: return other.value + self.value
		except AttributeError: return other + self.value
		
	def __eq__( self, other ):
		""" Returns true if the value of this word equals the value
			of the other word
		"""
		try: return other.value == self.value
		except AttributeError: return other == self.value
		
	def __hash__( self ):
		""" Hashes the word based on its value """
		return self.value.__hash__()
		
	
if __name__ == '__main__':
	word = PyWord("hello")
	word.config(syllables = 2)
	word.config(happy = True)
	print(list(word.config("syllables",'happy')))
	s = "hat"
	print()
	print(word+s)
	print(s+word)
	print(word,s)
	print(s,word)
	
	t = "hat"
	print(t==s)
	map = {t:1}
	print(map)
	map[s] = 2
	print(map)