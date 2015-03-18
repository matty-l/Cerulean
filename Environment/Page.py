"""
	This file contains the indiviudal pages used for editiing
	
	Author: Matthew Levine
	Date: 04/02/2015
"""

import tkinter.ttk as ttk
from ScrolledLinedText import ScrolledLinedText
from Scanner.Scanner import PyLex
from Scanner.Style import PyStyle
import tkinter as tk

from FindDialog import FindDialog
from GotoDialog import GotoDialog

import tkinter.filedialog as fileDialog


class PageList: 
	""" This class maintains several pages for editing """
	def __init__( self, notebook ):
		self.page_list = {}
		self.maxid = 0
		self.book = notebook
	
	def append( self, open=False, filename=None, run=lambda:0 ):
		""" Adds a new page to the list and returns it followed by its name"""
		id = self.maxid
		self.maxid += 1
		self.page_list[id] = Page( self.book ).build(open=open,filename=filename)
		
		# allow the page to be run using control-r
		self.page_list[id].input.bind("<Control-r>",
			lambda e:run(self.page_list[id].input.get('1.0',tk.END)))
		return self.page_list[id]
	
	def delete( self, *ids ):
		if ids[0] == 'all':
			for key in list(self.page_list.keys()): del self.page_list[key]
		else:
			for id in ids: del self.page_list[id]


class Page(ttk.Frame): 
	""" This class contains an individual page for editting """
	def build( self, open=False,filename = None ):
		""" Builds subwidgets within the page """
		self.grid_propagate(0)
		self.grid_rowconfigure(0,weight=1)
		self.grid_columnconfigure(0,weight=1)
		
		self._frame = ScrolledLinedText(self) # options defined statically in-widget
		self._frame.pack(side='top',fill='both',expand=1)
		self.input = self._frame.text
		
		# Populate the page; must have a location to write to
		try:
			if filename is not None:
				self.filename = filename
				self.open()
			elif not open:
				f = fileDialog.asksaveasfile(mode='w', defaultextension=".py")
				self.filename = f.name
			else:
				f = fileDialog.askopenfilename()
				self.filename=f
				self.open()
		except Exception as e:
			raise(e) # for now, don't let this happen since would probs be bug
			self.filename = '/_backup.py'
			
								
		self.input.bind("<Key>",self.reparse )
		# allow for redoing/undoing
		self.input.bind("<Control-z>",lambda e:self.edit_undo())
		self.input.bind("<Control-y>",lambda e:self.edit_redo())
		self.input.bind("<Control-f>",lambda e:self.find())
		self.input.bind("<Control-g>",lambda e:self.goto())
				
		# bind select-all
		def sel_all(event):
			self.input.tag_add(tk.SEL, "1.0", 'end')
			return "break"
		self.input.bind("<Control-a>",sel_all)
		
		self.text = ''
		
		for style,dic in PyStyle.styles().items():
			self.input.tag_configure(style,dic)
			

		self.find_index = '1.0'
		self.after(500,lambda:self._frame.line_numbers.redraw(force=1))			
			
		return self
				
	def edit_undo(self):
		""" Undoes one action in the text region 
		"""
		try:
			self.input.edit_undo()
		except: pass
		self.reparse(override=True)
	
	def edit_redo(self):
		"""Redoes one action in the text region """
		try:
			self.input.edit_redo()
		except: pass
		self.reparse(override=True)
	
	def open( self ):
		""" Opens a file and adds its contents to the widget """
		file = open(self.filename,'r')		
		for token in PyLex(file):
			self.input.insert(tk.END,token[0],token[2])
		file.close()
	
	def reparse( self, e=None, override=False, cursor=1 ):		
		""" Lexes an highlights text in the input
			
			Options:
			e (None) : tkinter text event. Certain events (like tab-key), are ignored
			override (False) : whether to force redraw and ignore escape-cases
			cursor (1) : if 0, does not move cursor on redraw
		"""
		
		def parse():
			# don't parse again if hasn't changed
			text = self.input.get('1.0',tk.END)
			if text == self.text and not override:
				return
			
			# ignore special keys
			if e is not None and not override:
				sym = e.keysym
				specials = ['space','Tab','Return','Shift_L','Shift_R','Backspace','Delete','Control_L','Control_R']
				if any((sym==special for special in specials)): 
					return	
				
			self.text = text
			
			cursor_position = self.input.index('insert')
				
			self.input.delete('1.0',tk.END)
			
			file = open(self.filename,'w')
			## FIXME: known bug here where whitespace is added, maybe use strip
			if len(text) > 0 and text[-1] == '\n':
				file.write(text[:-1])
			else:
				file.write(text)
			
			file.close()

			file = open(self.filename,'r')
			for token in PyLex(file):
				self.input.insert(tk.END,token[0],token[2])
			file.close()
			
			if cursor == True:
				self.input.mark_set('insert',cursor_position)	
				self.input.see(cursor_position)

		self.after(10,parse)
		
	def find( self ):
		""" Opens dialog to search current page for text """
		FindDialog.open(self)
		
	def goto( self ):
		""" Enables dialog for going to a given line """
		GotoDialog.open(self)