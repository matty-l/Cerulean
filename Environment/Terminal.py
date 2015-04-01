"""
	This class creates a terminal widget 
	
	Author: Matthew Levine
	Date: 09/13/2014
"""

from tkinter import Canvas,Text,END,INSERT,Scrollbar
from tkinter.scrolledtext import ScrolledText
import sys
from io import StringIO
import traceback
from threading import Timer

# for terminal access
import numpy
import math
from Environment.global_functions import get_default_functions, set_locals, set_terminal, get_nonlocals

# the keycode for backspaces
BACKSPACE = 22
RETURN = 36

# for noting changes in global
global_default = globals()

class PyTerminal:

	""" This class allows for direct access to system variables
		through a GUI option, managed by Tk.
	"""
	
	def __init__( self, root, master ):
		""" Initilaizes the terminal with the given root pane"""
		widgets = {'canvas':Canvas(root)}
		widgets.update({'entry':ScrolledText(widgets['canvas'],
			bg='black',fg='green',insertbackground='white')})
		self.__init_widgets(widgets)

		widgets['entry'].insert(INSERT,"Cerebro Terminal Online.\n>>")
		
		widgets['entry'].bind('<KeyRelease>',self.validate_line)
		widgets['entry'].bind('<Button-1>',self.validate_line)
		
		self.line_number = 2
		self.widgets = widgets
		self.master = master
		self.__delay__ = 0
		self.events = []
		
	def __init_widgets(self,widgets): 
		""" Initializes and manages widgets on scene """
		# widgets is a local variable on purpose. This method is really just
		# a subroutine at construction for clarity
		widgets['canvas'].pack(side='left',expand=1,fill='both')
		widgets['entry'].pack(expand=1,fill='both')
		
		def restrict_size(event):
			if widgets['canvas'].winfo_height() > 1:
				widgets['canvas'].config(height=0)
				widgets['canvas'].pack_propagate(0)
		widgets['canvas'].bind("<Configure>",restrict_size)

		
	def clear( self ):
		""" Clears text from the terminal """
		self.widgets['entry'].delete(2.0,END)
		self.widgets['entry'].insert(END,'\n>>')
		self.line_number = 2
		
	def __run(self, input="", internal=True):
		if internal: input=input.replace('self','self.master')
		old_out = sys.stdout
		new_out = sys.stdout = StringIO()
		try:
			if internal and input == 'exit()': exit(1)
			if internal and input == 'clear': 
				self.widgets['entry'].delete(2.0,END)
				self.widgets['entry'].insert(END,'\n')
				self.line_number = 2
				return
			
			# grab the built-in functions
			set_locals(globals())
			globals().update(get_nonlocals())
			set_terminal(self)
			globals().update(get_default_functions())
			captured = 1
			
			old_locals = locals().copy()
			# attempt to capture result
			try:
				exec ('result='+input,globals(),globals()) # execute the code
			except SyntaxError:
				captured = 0
			if not captured: # we don't want nested exceptions to print
				exec(input,globals(),globals())				
				
			for key,val in locals().items(): # save new variables
				if key != 'old_locals' and key not in old_locals:
					globals()[key] = val
			# remove default functions from globals
			for key in get_default_functions().keys():
				del globals()[key]
					
		except Exception as e:
			print('Cerebro Exception:',str(e),traceback.format_exc())
			
		output = new_out.getvalue()
		self.widgets['entry'].insert(END,'\n'+output)
		self.line_number += output.count('\n')+1
		self.widgets['entry'].see(END)
		
		sys.stdout = old_out
		self.widgets['entry'].see(END)
		
	def eval_next_line( self, event = None, line=None ):
		""" Evaluates the next line """
		entry = self.widgets['entry']
		
		index  = str(int((entry.index(INSERT)).split('.')[0])-1)
		
		# grab input if not provided
		if line is None:
			# error check
			if entry.get(index+'.0',index+'.2') != '>>':
				return entry.delete(index+'.0',index+'.999999')
			if int(index) != self.line_number: return
			self.line_number+=1
			
			# run the code
			self.__run(entry.get(index+'.2',index+'.9999999'))
		else:
			self.__run(line,internal=False)
		entry.insert('end','>>')
		
		# trigger observables
		[event(globals()) for event in self.events]
				
	def validate_line( self, event = None ):
		if event.keycode == RETURN:
			return self.eval_next_line(event)

		entry= self.widgets['entry']
		row,col = entry.index(INSERT).split('.')
		row_end,col_end = entry.index(END).split('.')
		
		# check backspace
		if int(col) < 2 and event.keycode == BACKSPACE:
			entry.insert(row+'.'+col,'>')
		# check typing to early
		if int(col) <= 2:
			entry.mark_set(INSERT,row+'.3')
		# check typing to early
		if int(row_end) != int(row):
			entry.mark_set(INSERT,row_end+'.3')
			
	def observe( self, event ):
		""" Triggers the event every time the terminal executes code """		
		self.events.append(event)

		
		
		
if __name__ == '__main__':
	import tkinter as tk
	root = tk.Tk()
	term = PyTerminal(root,None)
	root.mainloop()
	