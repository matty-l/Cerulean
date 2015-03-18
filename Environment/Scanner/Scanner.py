"""
	This file contains a Scanner/Lexer class.
	
	Author: Matthew Levine
	Date: 11/28/2014
"""

from Scanner.PyRules import Rule, getRules,CommentType
from Scanner.Token import PyToken, EOFToken, ErrorToken
from Scanner.TokenType import PyTokenType

class PyLex:
	""" Scanner/lexer reliant on the rules from the "Rules" module
	
		The lexer is an iterable over a parametrized file input stream.
	"""
	EOF = EOFToken()
	ERROR = ErrorToken()
	
	def __init__( self, iterable ):
		""" Builds a scanner from an iterable stream """
		self.stream = iterable.__iter__()
		self.__next__ = lambda : self.stream.read(1)
		self.rules = getRules()
		
	def __iter__( self ):
		""" Returns the next item in the stream """
		next_token = []
		valid_rules = self.rules[:]
		current_token = PyLex.ERROR
		error = 0
		
		while current_token is not PyLex.EOF:
			# get next token
			try:
				if error > 0:
					next_token.append(self.__next__())
				if len(next_token) > 0 and next_token[-1] == '': raise StopIteration()
			# no more tokens
			except StopIteration:
				if len(next_rules) >= 1:
					rule = next_rules[0]
					yield PyToken(''.join(next_token), rule )
				else:
					yield PyLex.EOF
				break
			
			next_rules = []
			
			for rule in valid_rules:
				if rule.could_match(''.join(next_token)): 
					next_rules.append(rule)
			
			# no rules match, use highest priority remaining rule
			if len(next_rules) == 0:
				final_token = ''.join(next_token[:-1])
				valid_rules = [r for r in valid_rules if r.matches(final_token)]				
				
				try:
					rule = valid_rules[0] if error > 0 else self.rules[-1]
				except IndexError:
					rule = getRules()[-1]
				# if rule.type is not CommentType:
				yield PyToken(final_token, rule) 
				del (next_token[:-1 if error > 0 else len(next_token)])
				# reset scan
				valid_rules = self.rules[:]
				error = 0
			# more than one rule still matches
			else:
				valid_rules = next_rules
				error += 1
	
	@staticmethod
	def is_visible( token ):
		""" Utility method for checking if a token is visible """
		return token.id > 9	
	
	@staticmethod
	def lookup_token_type( token ):
		""" Utility method fo reutrning the name of a token's type """
		return PyTokenType.lookup(token)