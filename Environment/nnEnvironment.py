"""
	This file contains a text editing environment for python code
	
	Author: Matthew Levine
	Date: 04/02/2015
"""

import tkinter as tk
import tkinter.ttk as ttk

from tkinter.font import Font as tkFont
import tkinter.filedialog as fileDialog

import pickle
import time
from multiprocessing import Process

import Terminal
from Page import PageList
from ModuleGrapher import ModuleGrapher

global_default = list(Terminal.global_default.keys())[:]

class DesktopController:
	""" This class contains the toplevel IDE environment controller """
	
	def __init__( self ):
		self.root = root = tk.Tk()
		root.title("Cerebro Environment")
		
		self.w = {}
		
		self.build_menu()

		self.build_variable_pane()
		self.build_execution_pane()
		self.build_notebook()
		
		self.root.protocol("WM_DELETE_WINDOW", self.close)
		self.root.bind("<Control-q>",self.close)
		
		self.reopen()
		root.mainloop()
		
	def close( self ):
		""" Closes the widget and save prefernces """
		# try: # this should be uncommented at deploy, but not for testing
		prefs = open('prefs.txt','w')
		# remember closed files and variables
		for id,page in self.w['left_frame']['notebook'].children.items():
			prefs.write(str(page.filename)+'\n')			
		prefs.close()
		# except: pass # can't crash here or program won't terminate
		
		self.root.destroy()
		
	def reopen( self ):
		""" Opens the last session """
		prefs = None
		try:
			prefs = open('prefs.txt','r')
		except IOError as e: print(e)
		for line in set(prefs):
			self.add_page(open=True,filename=line.replace('\n',''))
					
		if prefs is not None: prefs.close()
		
		
	def build_variable_pane(self):
		""" Builds the pane that displays current variables """
		self.w['right_frame'] = {
			'main' : tk.Frame(self.root,height=500,borderwidth=2,
				relief='sunken'),
		}
		rframe = self.w['right_frame']
		
		rframe['main'].pack(side='right',expand=0,fill='y')
		
		# what function to use when sorting the pane
		self.update_key = lambda e : e[0]
		self.reverse_key = 0 # what order to sort in
		
		def update_variable_pane(globals):
			""" Updates the variable pane """
			# clear current labels
			[el.grid_forget() for el in rframe['main'].grid_slaves()]
			
			# Allow viewing of variables
			def view_vars(event,globals=globals):
				if globals is None:
					return
				popup = tk.Toplevel()
				plottables = {key:val for key,
					val in globals.items() if key not in global_default}
				ModuleGrapher().graph(plottables,popup).pack()
				popup.mainloop()
				
			rframe['main'].bind("<Button-3>",view_vars)

			# title bar
			def setkey(newkey,x):
				""" Changes the function to use when sorting the pane """
				self.update_key = newkey
				self.reverse_key = not self.reverse_key
				self.update_variable_pane(globals)
				
			tk.Button(rframe['main'],width=10,height=0,text="Class",font='"DejaVu Sans" 9 bold',
				relief='sunken',borderwidth=1,
					command=lambda : setkey(lambda obj : str(type(obj[1]))[8:-2],'class') 
						).grid(row=0,column=0,sticky='ew')
			
			tk.Button(rframe['main'],width=10,text="Name",font='"DejaVu Sans" 9 bold',
				relief='sunken',borderwidth=2,
					command = lambda: setkey(lambda obj : obj[0],'name') 
						).grid(row=0,column=1,sticky='ew')
			
			tk.Button(rframe['main'],width=10,text="Value",font='"DejaVu Sans" 9 bold',
				relief='sunken',borderwidth=2,
					command=lambda: setkey(lambda obj :str(obj[1]),'value')
						).grid(row=0,column=2,sticky='ew')
	
			if globals is None: return
			i = 1 # we don't enumerate since it starts at 1

			for varname,variable in sorted(globals.items(),key=self.update_key,reverse=self.reverse_key):
				# don't list built-in variables
				if varname in global_default: continue

				# class of variable
				tk.Label(rframe['main'],text=str(type(variable))[8:-2],
					relief='sunken',borderwidth=2).grid(row=i,column=0,sticky='ew')
				# name of variable
				tk.Label(rframe['main'],text=varname,
					relief='sunken',borderwidth=2).grid(row=i,column=1,sticky='ew')
				# variable
				tk.Label(rframe['main'],text=str(variable)[:min(len(str(variable)),
					10)],relief='sunken',borderwidth=2).grid(row=i,column=2,sticky='ew')
				i += 1
			
		update_variable_pane(None)
		self.update_variable_pane = update_variable_pane
				
	def build_execution_pane(self):
		""" Builds the pane that displays the output from code execution """
		self.w['bottom_frame'] = {
			'main' : tk.Frame(self.root,width=750,height=100,borderwidth=2,
				relief='sunken'),
		}
		bframe = self.w['bottom_frame']
				
		bframe['terminal'] = Terminal.PyTerminal(bframe['main'],self)
		bframe['terminal'].observe(self.update_variable_pane)

		bframe['main'].pack(side='bottom',fill='both',expand=1)#row=1,column=0,sticky='nsew',columnspan=3)
		
		self.root.bind("<Control-p>",lambda e:bframe['terminal'].clear())

		
	def build_menu(self):
		""" Builds a menu for the environment """
		menu = self.w['menu'] = { 'main': tk.Menu(self.root) }
		self.w['menu'].update({
				'File':tk.Menu(menu['main'],tearoff=0),
				'Settings':tk.Menu(menu['main'],tearoff=0)
			})
		for name,item in sorted(self.w['menu'].items()):
			if item is not menu['main']:
				menu['main'].add_cascade(label=name,menu=item)
		
		actions = [ ('File','New',self.add_page),
					('File','Open',lambda:self.add_page(open=True)),
					('File','Close',lambda:self.close_page()),
					('Settings','Style',lambda:self.open_style())
				  ]
		
		for menu_name,name,event in actions:
			self.w['menu'][menu_name].add_command(label=name,command=event)
			
		self.root.config(menu=menu['main'])
		
	def open_style(self):
		""" Opens the style dialog """
		self.add_page(open=True,filename='Scanner/Style.py')
		
	def build_notebook( self ):
		""" Builds the notebook frame on the left """
		self.w['left_frame'] = {
			'main' : tk.Frame(self.root,borderwidth=2,width=500,height=500,
				relief='sunken'),
		}
		lframe = self.w['left_frame']

		lframe['notebook'] = ttk.Notebook(lframe['main'],width=500,height=500)
		lframe['pages'] = PageList(lframe['notebook'])
		
		self.root.bind('<Control-n>',lambda e:self.add_page())
		self.root.bind('<Control-o>',lambda e:self.add_page(open=True))
		self.root.bind('<Control-w>',lambda e:self.close_page())
		
		lframe['main'].pack(expand=1,fill='both',side='left')
		lframe['notebook'].pack(expand=1,fill='both')
		
		lframe['notebook'].enable_traversal()
		
	def add_page( self, open=False, filename=None ):
		""" Adds a blank page to the notebook in the left frame """
		lframe = self.w['left_frame']
		# changes and returns == bad OO
		tab = lframe['pages'].append(open=open,run=self.run_tab,filename=filename) 
		lframe['notebook'].add( tab, text=tab.filename.split('/')[-1])
	
	def close_page(self):
		""" Closes the current tab """
		book = self.w['left_frame']['notebook']
		del book.children[book.select().split('.')[-1]]
		book.forget(book.select())
		
	def get_current_page(self):
		""" Returns the page widget corresponding to the open tab """
		book = self.w['left_frame']['notebook']
		try:
			return book.children[book.select().split('.')[-1]]
		except KeyError:
			return None
		
	def run_tab( self, input ):
		""" Runs the code in the current tab by passing it (on a separate thread)
			to the terminal
		"""
		self.w['bottom_frame']['terminal'].eval_next_line(line=input)
		
		
if __name__ == '__main__':
	dc = DesktopController()
	