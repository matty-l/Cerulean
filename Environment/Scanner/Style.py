from operator import itemgetter

class PyStyle(str):
	""" This immutable class contains formatting options for Rules """
	
	
	@staticmethod
	def styles():
		return {'comment_style':	{'foreground':'#686868','font':'Consolas 10'},
				'keyword_style':	{'foreground':'#CC9900','font':'Consolas 10'},
				'self_style':		{'foreground':'light blue','font':'Consolas 10'},
				'operator_style':	{'foreground':'#CC9966','font':'Consolas 10 bold'},
				'string_style':		{'foreground':'#009966','font':'Consolas 10'},
				'doc_style':		{'foreground':'#666699','font':'Consolas 10'},
				'number_style':		{'foreground':'purple','font':'Consolas 10'},
				'literal_style':	{'foreground':'white','font':'Consolas 10'},
				'error_style':		{'foreground':'red','font':'Consolas 10 underline'}
			}