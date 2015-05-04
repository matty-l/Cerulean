"""
	This file contains methods to visualize error
	
	Author: Matthew Levine
	Date: 02/03/2015
"""
from utils.plotter import figure, plot, xlabel, ylabel, title, legend, subplot,\
							drawnow, get_statusbar

def nnupdatefigures(nn,fhandle,L,opts,i):
	""" Updates figures during training """
	if i > 1: # don't plot first point, it's only a point
		x_ax = range(i+1)
		# create legend
		if opts.validation == 1:
			M = tuple(("Training","Validation"))
		else:	
			M = tuple("Training")
			
		# create data for plots
		if nn.output == 'softmax':
			plot_x = x_ax # transpose? 
			plot_ye = L.train.e # transpose? 
			plot_yfrac = L.train.e_frac # transpose?
		else:
			plot_x = x_ax
			plot_ye = L.train.e
			
		# add error on validation data if present
		if opts.validation == 1:
			plot_x = plot_x + x_ax
			plot_ye = plot_ye + L.val.e
			
		# add classification error on validation data if present
		if opts.validation == 1:
			plot_x = plot_x + x_ax
			plot_ye = plot_ye + L.val.e
			
		# add classification error on validation data if present
		if opts.validation == 1 and nn.output == 'softmax':
			plot_yfrac = plot_yfrac + L.val.e_frac
			
		# plotting
		figure(fhandle)
		if nn.output == 'softmax':
			# subplot(1)

			plot(plot_x,[p for p in plot_yfrac])
			xlabel('Number of epochs')
			ylabel('Misclassification rate')
			title('Misclassification rate')
			# subplot(0)
		else:	
			plot(plot_x,plot_ye)
			xlabel('Number of epochs')
			ylabel('Error')
			title('Error')
		
		drawnow()
		
def nnupdatestatus(iter,maxiter):
	""" Checks for a global status bar; if it finds it, updates it with the
		iter value
	"""
	bar = get_statusbar()
	if bar is not None:
		bar['value'] = iter
		bar['maximum'] = maxiter
		bar.update()