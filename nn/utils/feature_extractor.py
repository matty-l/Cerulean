"""
	This file contains an image segmentation catalog
	
	Author: Matthew Levine
	Date: 03/15/2015
"""

import numpy as np
from scipy import ndimage
from scipy.misc import imread, toimage

import os
import time

path = 'C:/Users/Dev/Desktop/coil-20-proc'

def show(im):
	if __verbose__:
		toimage(im).show()
	
__verbose__ = 1

class FeatureExtractor:

	""" This class extracts features from images and handles associated
		io tasks
	"""

	NUM_FEATURES = 4
	
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
		
		# the imageset we're trying to reconstruct and how much to bias it
		self.target = 'obj21'
		self.bias = 21
		self.info = [ 0, 0, 0 ] # target, nontarget, total
		
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
		tag = fn.split('_')[0] if len(fn.split('_')) > 0 else ''

		for k in range( (tag == self.target) * self.bias + 1 ):
			# add to x
			if len(feature.shape) > 2:
				newf = np.zeros(shape=feature.shape[:-1])
				newf[:,:] = (feature[:,:,0] + feature[:,:,1] + feature[:,:,2])/3
				feature = newf
			self.features.append(feature.reshape(self.n*self.n))
			
			# add to y
			(lmap,lmax,dim) = self.labelmeta
			if tag not in lmap:
				lmap[tag] = lmax			
				self.labelmeta[1] += 1			
			
			self.labels.append( [ i==lmap[tag] for i in range(dim) ] )
			
		self.info[0] += (k != 0)
		self.info[1] += (k == 0)
		self.info[2] += 1
			
	def extract(self):
		""" Loops through the path-directory and extracts every image matching
			the pref's features
		"""
		maxiter = len(os.listdir(self.path))
		assert maxiter > 0, 'Invalid file; no images found'
		for j,fn in enumerate(os.listdir(self.path)):
			if self.fname == '' or fn.startswith(self.fname):
				if __verbose__:  print( str(j / maxiter * 100)[:5], ' : ', fn )
				im = imread(path+'/'+fn)
								
				for i,feature in enumerate((im,self.segment(im),self.gaussian(im),self.sob(im))):
					if i >= FeatureExtractor.NUM_FEATURES: break
					self.append(feature,fn=fn)				
				
		if __verbose__: print("Converting to numpy...")
		self.features = np.array(self.features)
		self.labels   = np.array(self.labels)
				
	def gaussian(self,im,blur=4):
		""" Applies gaussian blur to the image """
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

def test_extraction():
	""" Applies the extraction process """
	fe = FeatureExtractor(dim=128)
	t0 = time.time()
	fe.extract()
	tf = time.time() - t0
	print("Extracting...")
	print(fe.features.shape)
	print("Done Extracting")
	
	from scipy.io import savemat
	savemat('C:/Users/Dev/Desktop/ducky2',
		{'train_x':fe.features,'train_y':fe.labels})
		
	assert fe.info[0] + fe.info[1] == fe.info[2], 'Math error occurred in tracking'
	print("\nTrain_x dimension: ",fe.features.shape,
		  "\nTrain_y dimension: ",fe.labels.shape,
		  "\nTotal images processed", fe.info[2],
		  '\nTotal features processed',fe.info[0]*fe.bias+fe.info[1],
		  "\nTotal target images processed",fe.info[0],
		  "\nTotal non-target images processed",fe.info[1],
		  "\nRatio of target to non-target features:",fe.info[0]*fe.bias / (fe.info[0]*fe.bias+fe.info[1]) )
	print("Elapsed time:",str(tf)[:5])
if __name__ == '__main__':
	test_extraction()
	# from nninvert import test_recon
	# test_recon(fe.features,fe.get_solution(),dim=128,batches=81)