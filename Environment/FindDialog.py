"""
	This file contains a dialog that executes "find" functionality
	
	Author: Matthew Levine
	Date: 3/8/2015
"""

import tkinter as tk

class FindDialog:

	@staticmethod
	def open(self):
		pop = tk.Toplevel()
		pop.wm_overrideredirect(1)
		entry = tk.Entry(pop,width=20)
		entry.focus_set()
		entry.grid()
		
		# center the window
		pop.master.eval('tk::PlaceWindow %s center' % pop.winfo_pathname(pop.winfo_id()) )		
		
		def search(event=None):
			""" Searches for whatever text is currently in the entry """
			self.input.tag_remove('search','1.0','end')

			text = entry.get()
			# find it, then highlight it if found
			index = self.input.search(text,self.find_index)
			if index: 
				self.input.tag_add('search',index,index+'+'+str(len(text))+'c')
				self.find_index = index+'+'+str(len(text))+'c'
				self.input.mark_set("insert", "%d.%d" % (int(float(index)), 1))
				self.input.see(index)
			
			self.input.tag_config('search',background='#FF3399')

		def destroy(event=None):
			self.input.focus_set()
			pop.destroy()
			self.reparse(cursor=0,override=1)
			
				
		
		entry.bind("<Return>",search)
		entry.bind("<Escape>",destroy)