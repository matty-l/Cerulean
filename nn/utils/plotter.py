"""
	This file contains a simple line-plot module since matplotlib is the least
	portable package ever released. 
	
	The code in this file is entirely bare-bones plotting material, and should

	probably not be edited too extremely unless minimal additional support or
	tiny bug fixes are required. Switching to matplotlib is the far more
	extensible option.
	
	This file requires tkinter
	
	Author: Matthew Levine
	Date: 02/03/2015
"""

# don't touch these variables
handles = {} # dictionary of handles to figures
max_handle = 0 # largest figure handle 
cur_handle = 0 # current figure handle 


import tkinter as tk

def __fe(n):
	""" Internally used, formats strings into scientific notation """
	a = '%E' % n
	return a.split('E')[0].rstrip('0').rstrip('.')[:1] + 'e' + a.split('E')[1]

class __Figure:
	""" Figure manager class. This class should not be created by the user
		or accessed by the user
	"""

	def __init__( self ):
		""" Creates a new figure """
		if 'getRoot' in dir(tk):
			self.win = tk.getRoot()
		else:
			self.win = tk.Tk()
		self.frame = tk.Frame(self.win,relief='sunken',borderwidth=3)
				
		self.build()
				
		self.frame.grid(row=0,column=0)
		self.frames = 1
		self.win.title('Figure '+str(cur_handle))

		
	def build( self ):
		""" Builds a new plot in the current frame """
		(self.width,self.height) = (375,300)
		self.canvas = tk.Canvas(self.frame,width = self.width, height=self.height)
		self.title = tk.Label(self.frame)
		self.xlabel = tk.Label(self.frame)
		self.ylabel = tk.Label(self.frame,wraplength=1)
		self.legend = tk.Frame(self.frame)
		
		self.title.grid( row=0,column=1)
		self.canvas.grid(row=1,column=1)
		self.ylabel.grid(row=1,column=0)
		self.xlabel.grid(row=2,column=1)
		self.legend.grid(row=1,column=2)
		
		self.handle = cur_handle
		
		self.canvas.hold = False
		self.canvas.max = [0,0]

	
	def subplot( self, column = None ):
		""" Adds a new frame to the plot """
		self.frame = tk.Frame(self.win,relief='sunken',borderwidth=3)
		self.build()
		if column is None:
			self.frame.grid(row=0,column=self.frames)
			self.frames += 1
		else:
			self.frame.grid(row=0,column=column)
		
def figure(handle=None):
	""" Creates a new figure and returns its handle, or sets the current figure
		to the given handle. Only the current figure is ever acted on. Creating
		a figure automatically sets it to current.
	"""
	global max_handle, cur_handle
	
	if handle is None:
		handles[max_handle] = __Figure()
		cur_handle = max_handle
		max_handle += 1		
		return cur_handle
	else:
		cur_handle = handle
		
def legend(*text,color='black'): 
	""" Creates a legend with the given text and color, or texts and colors """
	leg = handles[cur_handle].legend
	try:
		if type('black') == type(''): raise TypeError('')
		for s,c in zip(text,color):
			tk.Label(leg,text=s,foreground=c).pack(side='bottom') # mixed managers
	except TypeError:
		for s in text:
			tk.Label(leg,text=s,foreground=color).pack(side='bottom')

def title(text):
	handles[cur_handle].title.configure(text=text)

def plot(X,Y,color='black'): 		
	""" Plots the current X and Y in a line plot, color optional, and adds
		tic marks on the axes. Will erase current drawing if "hold" is not
		set. Does not rescale if held.
	"""
	can = handles[cur_handle].canvas
	width,height = (handles[cur_handle].width,handles[cur_handle].height)
	
	X,Y = list(X),list(Y)
	
	assert len(X) == len(Y), "X and Y sets must match in dimension"
	maxX = max(X)
	maxY = max(Y)
	
	# if deleting the board, delete the board
	if not can.hold:
		can.delete('all')
		can.max = [0,0]

	# if we have new maxes, write them up
	if can.max == [0,0]:
		for i in range(5):
			if maxY/5*i < .01: # scientific notation if neccessary
				can.create_text(20,height//5*i+10,text=__fe(maxY/5*(5-i)))
			else:
				can.create_text(20,height//5*i+10,text=str(maxY/5*(5-i))[:4])
			can.create_text(width//5*i+20,height-20,text=str(maxX/5*i)[:3])

		can.max = [maxX,maxY]
	else:
		maxX = can.max[0]
		maxY = can.max[1]
	
	# plot the points
	(last_x,last_y) = (None,None)
	for x,y in zip(X,Y):
		new_x = x / maxX * (width-15) + 20
		new_y = height - (height * y/maxY) + 15
		can.create_oval( new_x-1, new_y-1, new_x+1, new_y+1, fill=color, outline=color )
		
		if last_x is not None and last_y is not None:
			can.create_line( last_x, last_y, new_x, new_y, fill=color )
		(last_x,last_y) = (new_x,new_y)
	
	
def xlabel(text):
	""" Adds the text to the x label """
	handles[cur_handle].xlabel.configure(text=text)
	
def ylabel(text):
	""" Adds the text to the ylabel """
	handles[cur_handle].ylabel.configure(text=text)
	
def hold():
	""" Tells the current canvas not to erase if another plot is drawn """
	handles[cur_handle].canvas.hold = True

def drawnow(hold=False):
	""" Renders all figures immediately """
	for handle, fig in handles.items():
		fig.win.update_idletasks()
	if hold:
		fig.win.mainloop()
	
		
def subplot(column=None):
	""" Indicates that the next plot should be drawn in the same window,
		next to the current plot
	"""
	handles[cur_handle].subplot(column)


def get_statusbar():
	""" Returns a tkinter status bar if it is defined, else None """
	try:
		return tk.status_bar
	except:
		return None

	
def testplot():
	from math import sin,cos,fabs,sqrt

	fhandle = figure()
	xlabel('X Axis')
	ylabel('Y Axis')
	X = list(range(50))
	Y = [fabs(sin(i)*i) for i in range(50)]
	plot(X,Y)
	
	h2 = figure()
	xlabel("New Axis X")
	ylabel("New Axis Y")
	X = list(range(100))
	Y = [i*i for i in range(100)]
	legend("X Squared",color='red')
	plot(X,Y,color='red')
	legend("X*sqrt(X)",color='blue')
	Y2 = [i*sqrt(i) for i in range(100)]
	hold()
	title("Compare")
	plot(X,Y2,color='blue')
	
	subplot()
	title("Contrast")
	xlabel('X Axis')
	ylabel('Y Axis')
	X = list(range(50))
	Y = [fabs(sin(i)*i) for i in range(50)]
	legend("Curve")
	plot(X,Y)	
	
	drawnow()
	
	tk.mainloop()
	
if __name__ == '__main__':
	# test code
	testplot()

