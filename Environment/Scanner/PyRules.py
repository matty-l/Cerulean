"""
	This file contains rule classes for scanning text. 
	
	This classes are not meant for package-external usage.
	
	Author: Matthew Levine
	Date: 11/28/2014
"""

import regex
from Scanner.Style import PyStyle
from Scanner.TokenType import PyTokenType
	
	
class Rule:
	""" This class contains rules for lexing """

	def __init__( self, code, id, style=''):
		""" Makes a new rule """
		self.re = regex.compile(code)
		self.type = id
		self.style = PyStyle(style)
		
	def could_match( self, other ):
		""" Returns true if other matches or partially matches the regex.
		"""
		match = self.re.match(other,partial=True)
		# the first line checks that there is either a match or partial match
		# the second line checks if it was a partial match
		# the third line allows for a complete match, which is not a match
		return match is not None\
			and (match.partial or
			match.endpos <= match.span()[1])
			
	def matches( self, other ):
		""" Returns true if the other matches the regex """
		match = self.re.match(other)
		return match is not None and match.span()[1] == len(other)
					
		
	def __repr__( self ):
		return "< Rule: "+self.re.pattern+" >"

class StringRule(Rule):
	""" This class is specially designed to handle strings """
	def could_match( self, other ):
		""" Returns other if the string matches python string rules.
			Part of this is done by regex, but the python definition of a 
			string
			
			https://docs.python.org/3/reference/lexical_analysis.html
			
			is more of a cfg than a regex. A cfg is overkill since we'll
			manually handle the few outlier cases. We note our own inneficiences
			in-line
		"""
		matches = Rule.could_match(self,other)
		# make sure no illegal escape characters
		if matches:
			# do not include escaped close-quotes
			if len(other) > 2 and other[-2] == '\\' and not (\
					len(other) > 3 and other[-3] == '\\'): 
				return False
			
			# sever the prefix
			if len(other) > 0 and other[0].lower() in ['r','u','b']:
				if len(other) > 1 and other[1].lower() in ['r','b']:
					sub = other[2:]
				else:
					sub = other[1:]
			else:
				sub = other
			
			if len(sub) == 0:
				return True
			open = sub[0]
			for i,c in enumerate(sub[1:-1]):
				if c == open and sub[i-1] != '\\':
					return False
			
			return True
			
		return False
		
rules = [
			Rule('#.*',PyTokenType.comment,style='comment_style'),

			Rule('\n',PyTokenType.new_line),

			Rule('self',PyTokenType.keyword, style='self_style'),
			
			Rule('(False)|(class)|(finally)|(is)|(None)|(contine)|(for)'+
				 '|(lambda)|(True)|(def)|(from)|(nonlocal)|(and)|(del)|'+
				 '(global)|(not)|(as)|(elif)|(if)|(or)|(assert)|(else)|'+
				 '(import)|(pass)|(break)|(except)|(in)|(raise)|(return)'+
				 '|(try)|(while)|(with)|(yield)', PyTokenType.keyword,
				 style='keyword_style'),
				 
			Rule('[a-zA-Z_][a-zA-Z_0-9]*',PyTokenType.literal,style='literal_style'),

			
			Rule('[ \t\r\f\v]+',PyTokenType.whitespace),
			
			Rule('(->)|(\+=)|(-=)|(\*=)|(/=)|(//=)|(%=)|(&=)|(\|=)|(\^=)'+\
				'|(>>=)|(<<=)|(\*\*=)'+\
				'|\(|\)|\[|\]|\{|\}|,|:|\.|;|@|=',
				PyTokenType.delimeter,style='operator_style'),
				
			Rule('(\*\*)|(//)|(<=)|(>=)|\+|-|\*|/|(%)|(<<)|(>>)|&'+\
				  '|\||\^|~|>|<|(==)|(!=)',
				  PyTokenType.operator,style='operator_style'),
				  
			Rule('(\d*\.\d*)|([0-9]+\.?)|(\.?[0-9]+)',PyTokenType.number, style='number_style'), 
				  
			StringRule('(r|u|R|U|b|B|(br)|(Br)|(BR)|(rb)|(rB)|(Rb)|(RB))?'+\
				 '[\'"].*',PyTokenType.string,style='string_style'),
				
			Rule('"""[^"]*"""',PyTokenType.string,style='doc_style'),
				 
			Rule('\$|\?',PyTokenType.LEX_ERROR,style='error_style')
		]
	
def getRules(): return rules



CommentType = PyTokenType.comment

def test_string_rule():
	""" Tests the string rule """
	s1 = '"Hello world! My name is matthew"' # normal doule quote
	s2 = "'Hello world! My name is matthew'" # normal single quote
	s3 = '"Hello world! " Hello Dog!"' # bad quote in middle
	s4 = '"Hello world! \" Hello DOg!"' # okay quote in middle
	s5 = '"Hello World! Holl Dog!\\"' # bad escape
	s6 = 'r"hello world"' # okay prefix
	s7 = 'q"Hello world"' # bad prefix
	
	ruleS = StringRule('(r|u|R|U|b|B|(br)|(Br)|(BR)|(rb)|(rB)|(Rb)|(RB))?'+\
				 '[\'"].*',PyTokenType.string)
	print(ruleS.could_match(s1),True)
	print(ruleS.could_match(s2),True)
	print(ruleS.could_match(s3),False)
	print(ruleS.could_match(s4),True)
	print(ruleS.could_match(s5),False)
	print(ruleS.could_match(s6),True)
	print(ruleS.could_match(s7),False)
	
def test_symbol_rules():
	s1 = [c for c in "()[]{},:.;@="]
	s2 = ['->','+=','-=','*=','/=','//=','%=','&=',
		'|=','^=','>>=','<<=','**=']
	s3 = [c for c in "+-*/%&|^~<>"]
	s4 = ['**','//','<<','>>','<=','>=','==','!=']
		
	delRule = Rule('(->)|(\+=)|(-=)|(\*=)|(/=)|(//=)|(%=)|(&=)|(\|=)|(\^=)'+\
				'|(>>=)|(<<=)|(\*\*=)'+\
				'|\(|\)|\[|\]|\{|\}|,|:|\.|;|@|=',
				PyTokenType.delimeter)
	opRule = Rule('(\*\*)|(//)|(<=)|(>=)|\+|-|\*|/|(%)|(<<)|(>>)|&'+\
				  '|\||\^|~|>|<|(==)|(!=)',
				  PyTokenType.operator)
				
	# delRule = Rule('[(){},:.;@=]|(\\])|(\\])'+\
				# '(\\->)|(\\+=)|(\\-=)|(\\*=)|(/=)|(//=)|(%=)'+\
				# '|(&=)|(\\|=)|(\\^=)|(>>=)|(<<=)|(\\*\\*=)',
				# PyTokenType.delimeter)

	for s in s1:
		print(delRule.could_match(s),s,opRule.could_match(s))
	print()
	for t in s2:
		print(delRule.could_match(t),t,opRule.could_match(t))
	print()
	for s in s3:
		print(opRule.could_match(s),s,delRule.could_match(s))
	print()
	for t in s4:
		print(opRule.could_match(t),t,delRule.could_match(t))
		
def test_numericals():
	s1 = ['1','1.','1.1','.1','11','.','1a1','hat']
	numerical_rule = Rule('(\d*\.\d*)|([0-9]+\.?)|(\.?[0-9]+)',PyTokenType.number)
	
	for s in s1:
		print(s,numerical_rule.could_match(s),numerical_rule.matches(s))
		
if __name__ == '__main__':
	import sys
	if len(sys.argv) > 1:
		if sys.argv[1] == 'string':
			test_string_rule()
		elif sys.argv[1] == 'symbol':
			test_symbol_rules()
		elif sys.argv[2] == 'number':
			test_numericals()
		else:
			print("No rule for",sys.argv[1])
	
		