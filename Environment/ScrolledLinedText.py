"""
	This class wraps a widget for a scolling text-widget with line numbers.
	
	The line-numbers are based on an effect described by Bryan Oakley here:
	http://stackoverflow.com/questions/16369470/tkinter-adding-line-number-to-text-widget
	
	Author: Matthew Levine
	Date: 03/08/2015
"""

import tkinter as tk
# from tkinter.scrolledtext import ScrolledText
from tkinter.font import Font as tkFont

class TextLineNumbers(tk.Canvas):
	""" This canvas extension draws line numbers vertically """
	def __init__(self, *args, **kwargs):
		tk.Canvas.__init__(self, *args, **kwargs)
		self.textwidget = None
		self.last_i = -1

	def attach(self, text_widget):
		self.textwidget = text_widget

	def redraw(self, force = False):
		'''redraw line numbers'''
		
		i = self.textwidget.index("@0,0")
		if (not force) and i == self.last_i:
			return
		self.last_i = i

		self.delete("all")
		
		while True :
			dline= self.textwidget.dlineinfo(i)
			if dline is None: break
			y = dline[1]
			linenum = str(i).split(".")[0]
			self.create_text(2,y,anchor="nw", text=linenum)
			i = self.textwidget.index("%s+1line" % i)
			
class ChangeLoggedText(tk.Text):
	""" This extension of scrolled-text widget has additional events in order
		to track line numbers
	"""
	def __init__(self, *args, **kwargs):
		tk.Text.__init__(self, *args, **kwargs)

		self.tk.eval('''
			proc widget_proxy {widget widget_command args} {

				# call the real tk widget command with the real args
				set result [uplevel [linsert $args 0 $widget_command]]

				# generate the event for certain types of commands
				if {([lindex $args 0] in {insert replace delete}) ||
					([lrange $args 0 2] == {mark set insert}) || 
					([lrange $args 0 1] == {xview moveto}) ||
					([lrange $args 0 1] == {xview scroll}) ||
					([lrange $args 0 1] == {yview moveto}) ||
					([lrange $args 0 1] == {yview scroll})} {

					event generate	$widget <<Change>> -when tail
				}

				# return the result from the real widget command
				return $result
			}
			''')
		self.tk.eval('''
			rename {widget} _{widget}
			interp alias {{}} ::{widget} {{}} widget_proxy {widget} _{widget}
		'''.format(widget=str(self)))	
		

class ScrolledLinedText(tk.Frame):
	""" This class contains a text widget that has a vertical scrollbar on the
		right and line numbers on the left
	"""
		
	def __init__(self, *args, **kwargs):
		tk.Frame.__init__(self, *args, **kwargs)
		# these should probably be parameterized
		self.text = ChangeLoggedText(self,background='black',insertbackground='white',
			font=tkFont(family='Consolas',size=7),undo=1,wrap='word')
		vsb = tk.Scrollbar(self,orient='vertical',command=self.text.yview)
		self.text.configure(yscrollcommand=vsb.set)
			
		self.line_numbers = TextLineNumbers(self, width=30)
		self.line_numbers.attach(self.text)
		vsb.pack(side='right',fill='y')
		self.line_numbers.pack(side="left", fill="y")
		self.text.pack(side="right", fill="both", expand=True)

		self.text.bind("<<Change>>", lambda e : self.line_numbers.redraw())
		self.text.bind("<Configure>", lambda e : self.line_numbers.redraw())
		

if __name__ == "__main__":
	root = tk.Tk()
	ScrolledLinedText(root).pack()
	root.mainloop()
