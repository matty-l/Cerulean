"""
	This file contains an image segmentation catalog
	
	Author: Matthew Levine
	Date: 03/15/2015
"""

import numpy as np
from scipy import ndimage
from scipy.misc import imread, toimage

import os

path = 'C:/Users/Dev/Desktop/Cerebro2/images/coil-20-proc'

def show(im):
	if __verbose__:
		toimage(im).show()
	
__verbose__ = 1

class FeatureExtractor:

	""" This class extracts features from images and handles associated
		io tasks
	"""

	def __init__( self, directory=path, pref='', dim=28):
		""" Make a new feature extractor
		
			Directory - the location of the images
			pref	  - the prefix on the images (before an underscore)
			dim		  - the dimension of the images
		"""
		self.path = directory
		self.fname = pref
		self.features = []
		
		self.labels   = []		
		self.labelmeta = [{},0,self.getYDim()]
		# self.labelmap = {}
		# self.labelmax = 0
		# self.ydim = self.getYDim()
		
		self.n = dim
		
	def getYDim( self ):
		""" Computes (not O(1)) the y dimension of the proposed data """
		img_set = {}
		for fn in os.listdir(self.path):
			tag = fn.split("_")
			if len(tag) > 0 and tag[0] not in img_set:
				img_set[tag[0]] = 1
		return len(img_set)
		
	def append(self,feature,fn=''):
		""" Adds the given feature to the feature list """
		# add to x
		self.features.append(feature.reshape(self.n*self.n))
		
		# add to y
		tag = fn.split('_')[0] if len(fn.split('_')) > 0 else ''
		(lmap,lmax,dim) = self.labelmeta
		if tag not in lmap:
			lmap[tag] = lmax
			self.labelmeta[1] += 1
		
		self.labels.append( [ i==lmap[tag] for i in range(dim) ] )
			
	def extract(self):
		""" Loops through the path-directory and extracts every image matching
			the pref's features
		"""
		for fn in os.listdir(self.path):
			if self.fname == '' or fn.startswith(self.fname):
				if __verbose__:
					print(fn)
				im = imread(path+'/'+fn)
				
				# show(im)
				
				for feature in (im,self.gaussian(im),self.sob(im),self.segment(im)):
					self.append(feature,fn=fn)
				# self.append(self.gaussian(im))
				# self.append(self.sob(im))
				# for thresh in range(2,8):
					# self.append(self.segment(im,thresh=thresh/10))
					# show(self.features[-1])
												
				# show(im)				
				
		self.features = np.array(self.features)
		self.labels   = np.array(self.labels)
				
	def gaussian(self,im,blur=4):
		""" Applies gaussian blur to the image """
		# ndimage.rotate(im,15,mode='constant')
		return ndimage.gaussian_filter(im,4)
		
	def sob(self,im):
		""" Applies sob filter to the image """
		sx = ndimage.sobel(im,axis=0,mode='constant')
		sy = ndimage.sobel(im,axis=1,mode='constant')
		return np.hypot(sx,sy)
		
	def segment(self,im,n=10,thresh=.5):
		""" Applies segmentation computation """
		im = ndimage.gaussian_filter(im,sigma=1/(4.*n))
		mask = (im > im.mean()).astype(np.float)
		mask += .1 * im
		img = mask + .2*np.random.randn(*mask.shape)
		return img > thresh
		
	def get_trivial_solution( self ):
		""" Returns a trivial y-solution corresponding to the dimension
			of the input space
		"""
		return np.zeros((self.features.shape[0],1))

				
if __name__ == '__main__':
	fe = FeatureExtractor(dim=128)
	fe.extract()
	print("Extracting...")
	print(fe.features.shape)
	print("Done Extracting")
	
	from scipy.io import savemat
	savemat('ducky',{'train_x':fe.features,'train_y':fe.labels})
	
	# from nninvert import test_recon
	# test_recon(fe.features,fe.get_solution(),dim=128,batches=81)