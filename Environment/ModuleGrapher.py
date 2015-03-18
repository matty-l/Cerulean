"""
	This file contains a function that graphs a class structure
	
	Author: Matthew Levine
	Date: 03/08/2015
"""

import tkinter as tk
import random


class ColorTable:

	""" This class allows for random but consistent seeding of hex colors
		
		The colors are not distributed in any special way, say to be
		ascetically pleasing. They also probably have a tendency to be grayish.
		
		Retrieving a color is amortized O(1)
	"""

	def __init__(self):
		self.i = 0
		self.color_table = [self.__next_color() for i in range(10)]
		
	def reset(self):
		""" Rests the table index to return the first color in the table """
		self.i = 0
		
	def next_color(self):
		""" Returns the next color in the table """
		# double table if out of colors
		if self.i >= len(self.color_table):
			l = len(self.color_table)
			self.color_table += [self.__next_color() for i in range(l)]
		
		color = self.color_table[self.i]
		self.i += 1
		return color

		
	def __next_color(self):	
		""" Returns a randomish hex-color. Not for external use """
		r = lambda: random.randint(30,235)
		return '#%02X%02X%02X' % (r(),r(),r())

		
CR = 40
CD = 100

NAMES = 1
TYPES = 0

class Level:
	""" This class maintains a depth-integer and a list of items mapped
		at a certain recursion in the graph
	"""
	def __init__(self,n):
		self.n = 0
		self.items = {}
		
	def add_item(self,item):
		""" Adds an item to this level """
		self.items[item] = 1
		
	def adjust(self,n):
		""" Adjusts the maximal x-offset in this level """
		if n > self.n:
			self.n = n
			
	def __repr__(self):
		return "<Depth : "+str(self.n)+">"

class ModuleGrapher:

	""" This class creates graphs of namespaces """
	
	def __init__( self ):
		self.colors = ColorTable()
		self.graphing = NAMES

	def graph( self, globals, root ):
		""" Returns a canvas with a graph of the relationship between items in globals """
		frame = tk.Frame(root,width=750,height=750)
		
		self.canvas = tk.Canvas(frame,width=700,height=700,
									scrollregion=(0,0,2800,2800))
		# add the scrollbars
		hbar,vbar = (tk.Scrollbar(frame,orient=o) for o in ('horizontal','vertical'))
		(hbar.pack(side='bottom',fill='x'),vbar.pack(side='right',fill='y'))
		hbar.config(command=self.canvas.xview)
		vbar.config(command=self.canvas.yview)
		self.canvas.config(width=700,height=700,xscrollcommand=hbar.set,
							yscrollcommand=vbar.set)

		self.canvas.pack(side='left',expand=1,fill='both')
		
		# this dictionary maps how many children are maximally spawned from
		# an existing node at a given level; equivalently, it indicates the 
		# x-offset we need when plotting a new node at a given level
		self.levels = {} 
		self.items =  {}
		
		self.plot(globals,0)
		# self.canvas.update()
		# self.canvas.postscript(file="im.ps", colormode='color')

		self.__data = globals # FIXME: should do some sort of weakref with subclasses
		self.canvas.bind("<Button-1>",self.regraph)
				
		return frame
		
	def regraph( self, event ):
		""" Regraphs the original input; if previously type, graphs with
			names and visa versa
		"""
		self.graphing = TYPES if self.graphing else NAMES
		self.canvas.delete('all')
		self.colors.reset()
		self.levels = {}
		self.items =  {}
		self.plot(self.__data,0)
		
	def plot( self, dictionary, level, color=None, origin=None, category='instance' ):
		""" Plots the dictionary on the canvas at the current level
			
			Cannot recurse on unhashable types
		"""
		if level not in self.levels:
			self.levels[level] = Level(0)
		
		for name, value in dictionary.items():
			if '__' in name: continue # skip hidden vars
			x = self.levels[level].n
			xprev = self.levels[level+1].n if level+1 in self.levels else -1
			x = max(x,xprev)

			(xpos,ypos) = self.get_coordinates_of_value(value)

			# if we haven't seen it, plot it at a new point
			if (xpos,ypos) == (None,None):
				# mark the spot
				if level == 0:
					color = self.colors.next_color()
								
				if category == 'instance':
					self.canvas.create_oval( (x+1)*CD-CR, (level+1)*CD-CR,
									(x+1)*CD+CR, (level+1)*CD+CR,fill=color )
				elif category == 'class':
					self.canvas.create_rectangle( (x+1)*CD-CR, (level+1)*CD-CR,
									(x+1)*CD+CR, (level+1)*CD+CR,fill=color )
				else:
					raise Exception("Invalid category parameter")
				
				disp = name if self.graphing else str(type(value))[8:-2]
				self.canvas.create_text( (x+1)*CD, (level+1)*CD, 
									text=disp[:12], font='Helvetica 8' )
				
				# link the nodes
				if origin is not None:
					self.canvas.create_line(origin[0],origin[1],
									(x+1)*CD,(level+1)*CD,arrow='last')
			
			# otherwise, link to the old point
			elif origin is not None:
				self.canvas.create_line(origin[0],origin[1],
								xpos,ypos,arrow='last',fill='blue')
			
			
			# pass on this point as a "parent", if it was actually a new item
			if (xpos,ypos) == (None,None):
				origin_next = tuple(((x+1)*CD, (level+1)*CD))
				self.levels[level].adjust(x+1)				
			else:
				origin_next = None
								
			# depth-first search on plot, but not int, str, etc. bc we know them
			if type(value) not in (int,str,bool,float,list,tuple,dict):														
				if level < 10 and hasattr(value,'__dict__'):	
					self.plot( value.__dict__, level + 1, color, origin=origin_next )
				if level < 10 and hasattr(value.__class__,'__dict__'):	
					self.plot( value.__class__.__dict__, 
						level + 1, color, origin=origin_next, category='class' )
			
			if (xpos,ypos) == (None,None):
				try:
					self.items[value] = origin_next
				except TypeError:
					self.items[str(value)] = origin_next
				
	def get_coordinates_of_value(self,value):
		""" Returns the coordinates of the value or none if the value has
			not been coordinitized. If the value is unhashable, may return
			the wrong coordinates. 
			
			Note that typical reasons for not hashing
			don't typically apply unless in threaded applications, since the
			chances of, say, a lists values changing and leaving a memory
			leak, are extremely low. Even if they did occur, the mem-leak would
			be small and short lived
		"""
		(xpos,ypos) = (None,None)
		try:
			# if we've already seen this item, grab it's existing coords
			if value in self.items: # implicetly must be hashable
				(xpos,ypos) = self.items[value]
		# It wasn't hashable; try harder to find it and risk mistakes
		except TypeError:
			if str(value) in self.items:
				(xpos,ypos) = self.items[str(value)]
		
		return (xpos,ypos)
			
class Foo:

	def __init__(self):
		self.x = 3
		self.y = 4
		self.z = 5
		self.xyz = 345
		self.bar = Bar()
		
class Bar:
	def __init__(self):
		self.a = -1
		self.b = -2
		
	def bar():
		print('hello world')
			
if __name__ == '__main__':
	root = tk.Tk()
	mg = ModuleGrapher()
	fakespace = {'g':Bar(),'f':Foo()}
	mg.graph(globals(),root).pack()
	root.mainloop()