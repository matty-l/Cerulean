"""
	This file contains a profiling gui
	
	Author: Matthew Levine
	Date: 03/31/2015
"""

import profile
import tkinter as tk
from io import StringIO
import sys
import time

class ProfileDisplay(tk.Frame):
	"This clas maages output from the profiler in a widget form """
	
	def __init__( self, root, width=600, height=300, **kwargs ):
		tk.Frame.__init__(self,root,**kwargs)
		self.config(bg='white')
		
		self.profile_headers = ['Num Calls','Total Time','Total Time Per Call',
			'Cummulative Time','Cum. Time Per Call', 'Function']
		HX = len(self.profile_headers)
		
		# add sub-widgets, scrollbars and main canvas
		self.page = tk.Canvas(self,width=600,height=300,
			scrollregion=(0,0,2000,2000), bg='white')
		
		hbar = tk.Scrollbar(self,orient='horizontal')
		hbar.grid(row=2,column=0,columnspan=HX-1,sticky='ew')
		hbar.config(command=self.page.xview)
		
		vbar = tk.Scrollbar(self,orient='vertical')
		vbar.grid(row=1,column=HX,sticky='ns')
		vbar.config(command=self.page.yview)
		
		self.page.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
		self.page.grid(row=1,column=0,columnspan=HX-1,sticky='nsew')
		
		
		# table fields
		self.headers = []
		self.table = []
		self.profile_out = ''
		self.sort_index = -1
		self.reversed = 0
		self.total_time = 0
		
		self.update_headers()
	
		
	def update_headers( self ):
		""" Adds or updates headers """
		for button in self.headers:
			button.grid_forget()
		
		comp = { item:i for i,item in enumerate(self.profile_headers) }


		curOpt = tk.StringVar(self.master)
		curOpt.set('Sort Preference (Time: '+str(self.total_time)[:5]+')')

		sort_opts = tk.OptionMenu( self.master, curOpt, *self.profile_headers)
		curOpt.trace( 'w', lambda a,b,c:self.sort(comp[curOpt.get()]) )
		
		sort_opts.grid(row=0)
		self.headers.append(sort_opts)
		
	def sort( self, col_index ):
		self.sort_index = col_index
		self.update_table()
		
	def profile( self, function ):
		""" Runs the function and displays its profile output 		
		
			Things normally printed during function execution will not be 
			printed to stdout
		"""
		# setup profiling
		assert '_function_' not in globals(), 'Bad naming conventions thwarted profiler'
		globals()['_function_'] = function 		
		__builtins__['_function_'] = function

		old_out = sys.stdout
		new_out = sys.stdout = StringIO()

		# profile and write to gui
		t0 = time.time()
		profile.run('_function_()')
		tf = time.time() - t0
		sys.stdout = old_out
		profile_out = new_out.getvalue()
		self.profile_out = profile_out.split('(function)')[1]
		
		self.update_table()
		self.total_time = tf	
		self.update_headers()
		
		# cleanup
		assert '_function_' in globals(), 'The profile complete successfully but crashed in cleanup'
		del globals()['_function_']
		del __builtins__['_function_']

		def toggle(event=None):
			self.reversed = not self.reversed
			self.update_table()
		self.bind("<r>",toggle)		
		
	def update_table( self ):
		""" Updates the text in the table view with the last profile information
		"""
		self.page.delete('all')
		
		for col,item in enumerate(self.profile_headers):
			self.page.create_text(50+col*200,20,text=item)
			
		# Sort the content
		context = [ [el for el in line.split(' ') if el.strip() != ''] for line in self.profile_out.split('\n') ]
		context = [ col for col in context if len(col) > 0 ]
		if self.sort_index >= 0:
			def key(col):
				if len(col) > self.sort_index:
					try: return float(col[self.sort_index])
					except ValueError: return col[0]
				else: sys.maxsize
			try:
				context = sorted(context,key=key,reverse=self.reversed)
				self.reversed = not self.reversed
			except TypeError: pass
		
		# Display it
		for row,line in enumerate(context): # lots of magic "heurstic" #s
			for col,word in enumerate(line):
				self.page.create_text( 50+col*200,  20+(row+1)*20, text = word )	
				self.page.create_line( 0, col*20+7, 2000, col*20+7 )
			self.page.create_line( (row+1)*200-50,0,(row+1)*200-50,2000)
		
def display_profile( function ):
	""" Produces popup with given function profiled """
	pd = ProfileDisplay(tk.Toplevel())
	pd.grid()
	
	pd.profile(function)
	
		
if __name__ == '__main__':
	pd = ProfileDisplay(tk.Tk(), width =500, height=500)
	pd.grid()
	
	import time
	
	def sillyfunc():
		def billyfunc():
			for i in range(10000000):pass
		time.sleep(2)
		billyfunc()
	
	pd.profile(sillyfunc)
	pd.master.mainloop()