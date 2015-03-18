"""
	This file contains a dialog that executes "goto" functionality
	
	Author: Matthew Levine
	Date: 3/8/2015

"""
import tkinter as tk

class GotoDialog:

	@staticmethod
	def open(self):
		# make a window
		pop = tk.Toplevel()
		pop.wm_overrideredirect(1)
		entry = tk.Entry(pop,width=20)
		entry.focus_set()
		entry.grid()
		
		# center the window
		pop.master.eval('tk::PlaceWindow %s center' % pop.winfo_pathname(pop.winfo_id()) )		

		def search_line(event=None):
			""" Searches for whatever text is currently in the entry """
			try:
				line_i = int(entry.get())
				line = str(line_i)+'.0'
			except:
				return

			self.input.focus_set()
			self.input.mark_set("insert", "%d.%d" % (line_i, 1))
			self.input.see(line)
				
			line_end = self.input.index("%s lineend" % line)
			# self.input.tag_remove("line_goto", 1.0, "end")
			# self.input.tag_configure('line_goto',background='#FF3399')
			# self.input.tag_add("line_goto", line, line_end)
			
			pop.destroy()
			
		def destroy(event=None):
			pop.destroy()
			self.reparse(cursor=0,override=1)
			self.input.focus_set()
				
		entry.bind("<Return>",search_line)
		entry.bind("<Escape>",destroy)