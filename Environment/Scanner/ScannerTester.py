

sample_code = """ 
class TestCode:
	def function( self ):
		print( "Hello World" )
		
	def foo( a, b, c):
		print( a + b + c )
		a = b + c
		a - b << c |= d
		
		if foo == bar: print(foo)
		
"""

from Scanner import PyLex

if __name__ == '__main__':
	file = open('sample_code.py','w')
	file.write(sample_code)
	file.close()
	
	file = open('sample_code.py','r')
	scan = PyLex(file)
	for tok in scan:
		print(PyLex.lookup_token_type(tok),' ---- ',tok)
	
	file.close()
		
