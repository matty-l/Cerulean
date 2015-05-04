"""
	This file contains a list of global utility functions accessible
	to the user.
	
	Author: Matthew Levine
	Date: 3/6/2015
"""

# __future__
# - Add an edit/open function for terminal access? Ugly dependencies though.
# - Clean up deprecated functions

import tkinter as tk
import sys
import os
import inspect

__locals = {}
__nonlocals = {}
terminal = None

def get_default_functions():
	""" Returns a list of default functions """		
	return {'cls':cls,'add_path':add_path,'debug':debug}

def set_locals( new_locals ):
	""" Sets the module-level pointer to a new namespace """
	global __locals
	__locals = new_locals
	
def get_nonlocals():
	return __nonlocals
	
def set_terminal( self ):
	""" Sets the module level pointer to a terminal """
	global terminal
	terminal = self

def cls(*var_names):
	""" Erases all variables from the global directory, or a specific
		variable name(s) if provided
	"""
	global __locals
	
	# if len(var_names) == 0:
		# __locals.clear()
	# else:
	for var_name in var_names:
		del __locals[var_name]
		
def add_path(pathname=''):
	sys.path.append(os.getcwd()+'/'+pathname)
	
# Should this really be here?
add_path('nn')
	
def debug(): # don't think this works right
	""" Stops execution mid-line and updates variable pane, allowing viewable
		of program progress and access to variables through terminal.
		
		Right now, progrress doesn't continue after
	"""
	global terminal,__nonlocals
	if terminal is None:
		raise BuiltinFunctionException("Misconfigured debug-mode")
	
	toplevel = tk.Toplevel(width=100,height=100)
	entry = tk.Entry(toplevel)
	
	__nonlocals = inspect.stack()[1][0].f_locals
	toplevel.after(1000,lambda:terminal.eval_next_line('print(1129832)'))
	entry.bind("<Return>",lambda e:terminal.eval_next_line(line=entry.get()))
	entry.pack(side='top',expand=1,fill='both')
	
	toplevel.mainloop()
		
	
def view():
	""" Produces a popup view of the variable graph

		FIXME: INCOMPLETE
		
		EDIT: there is now other functionality that does this
	"""
	win = tk.Toplevel()
	global __locals
	
	for name,value in __locals.items():
		print(name,value)
	
class BuiltinFunctionException(Exception): pass