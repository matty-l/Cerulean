opts = Opts()
opts.batchsize = 50
opts.numepochs
opts.plot=1

from nnsetup import nnsetup
from numpy import array,float
from random import random
from scipy.io import loadmat
print("Loading data")
result = loadmat("../mnist_uint8.mat")


nn = nnsetup([784,100,10])

x = result['train_x'].astype(float)/255
y = result['train_y'].astype(float)/255

# sample
x = x[:1000,:]
y = y[:1000,:]

print( "training data")

nntrain(nn,x,y,opts)

for property in nn.properties():
	print(property)

from plotter import drawnow
drawnow(1)


#def start():
#	import sys
#	def addpath(path):
#		sys.path.append(path)
#
#
#
#	from nntrain import *