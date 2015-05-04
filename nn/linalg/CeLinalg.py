"""
	This file is a Python wrapper on fast matrix operations done in C
	on numpy arrays.
	
	The external part of these functions are written
	as library access, with minimal OO support. This
	was an explicit decision not to extend numpy (though to use naming
	conventions that clarify which functions are being replaced). This is in part
	for	clarity - we don't want to pass around a new matrix wrapper masquerading
	as a numpy matrix when numpy matrices are far more common, but moreover 
	because it is still always preferable to use standard numpy operations built
	on BLAS when speed isn't utmostly vital.
	
	See the underlying C source for further documentation and exposition.
	The C code is an O(n^3) time complexity, parallelized and blocked. In timing,
	Strassen was slower than simpler algorithm, though Huss-Lederman suggests
	that Strassen can win with extremely effective memory management. This was
	not considered worth the investment, especially because it is particularly
	difficult to move Strassen to the GPU. Care is taken by the algortihm to 
	be memory cohesive.
	
	In timing, CeLinalg tends to be several times faster than numpy, especially
	in the long run when the adaptive thread sampling can optimize performance.
	It is still many times slower than Matlab's implementation.
	
	import __future__
	GPU enabled
	adaptive block division
	
	Author: Matthew Levine
	Date: 04/07/2015
"""

try:
	import linalg.CaLalg as CaLalg
except ImportError:
	try: import CaLalg
	except ImportError:
		raise Exception("You must compile (and include locally) the linalg Python extension package")
	
	
import numpy as np
from scipy.linalg import get_blas_funcs
from numpy.random import normal
import time

__validate__ = False
	
class Errors:
	""" Factory for errors in CeLinalg """
	def get(code):
		dot_product_errors = {1:"Wrong argument type",2:"Matrix dimension mismatch",
						3:"Output matrix wrong size"}
		if code in dot_product_errors:
			return dot_product_errors[code]
		return "Root cause unknown"
		
	@staticmethod
	def stat(*Ms):
		""" Returns useful information for identifying matrices, not content
			based
		"""
		return '\n'+'\n'.join([ ' '.join(['[',str(M.shape),str(M.flags),']']) for M in Ms])
		

class ThreadPool(object):
	""" This class manages threads for matrix multiplication optimization.
	"""
	
	MAX_THREAD_COUNT = 50
	OPTIMAL_THREAD = 4 # a guess
	__SINGLE__ = 0
	BLOCKS = 1

	
	def __init__(self):
		self.map = [0 for i in range(ThreadPool.MAX_THREAD_COUNT)]
		self.utl = [0 for i in range(ThreadPool.MAX_THREAD_COUNT)]
		# very weakly enforced singleton design, more "suggestion"
		assert ThreadPool.__SINGLE__ == 0
		ThreadPool.__SINGLE__ = 1
		
	
	def update( self, tid, time ):
		assert len(self.map) >= tid, 'Requested more threads than allowed'
		x,u = self.map[tid],self.utl[tid]
		self.map[tid] = (x*u+time)/(u+1)
		self.utl[tid] += 1
			
	def time(self, event):
		""" Times the arguless event """
		# guess a thread id or pick the initial guess if not enough info
		try:
			std = max(np.std(self.map) * 10,2)
			ave = np.argmin([r for r in self.map if r > 0],axis=0)
			tid = normal( loc=ave, scale=std )
			tid = min(int(abs(tid) + 1),len(self.map)-1)
			
		except ValueError:
			tid = ThreadPool.OPTIMAL_THREAD
		t0 = time.time()
		result = event(tid,ThreadPool.BLOCKS*50 + (not ThreadPool.BLOCKS)) # FIXME adaptive blocks
		
		self.update(tid,time.time()-t0)
		return result
		
	def display(self):
		""" Displays the map """
		s = ''
		for u,(i,t) in zip(self.utl,enumerate(self.map)):
			su,si,st = str(u),str(i),str(t)
			s += ' '.join([si,'threads','average',st,'seconds','applied',su,'times','\n'])
		return s
			
	def __del__( self ):
		""" Cleans up object """
		# try:
		file = open('linalg_log.log','a')
		breakp = ''.join(['-']*50)
		file.write('\n\n'+breakp+'\n')
		file.write(self.display())
		file.write('\n\n'+breakp)
		file.close()
		# except: pass # really can't have this cause any trouble during shutdown
			
__POOL__ = ThreadPool()	

def use_blocks(flag):	
	__POOL__.blocks = flag

def cdot( A, B ):
	C = np.zeros((A.shape[0],B.shape[1]))
	
	# is this really the best way to handle this?
	if not A.flags['C_CONTIGUOUS']:
		A = np.ascontiguousarray(A)
	if not B.flags['C_CONTIGUOUS']:
		B = np.ascontiguousarray(B)
	
	result = __POOL__.time(lambda threads,blocks:CaLalg.multiply(A,B,C,threads,blocks))
	
	if __validate__:
		debug = np.dot(A,B)
		assert np.all(debug==C), 'ERR: failed to correctly multiply matrices :'+Errors.stat(A,B)
	
	if result: raise Exception(Errors.get(result))
	
	return C
	
def dot( A, B ):
	""" This function guarantees that matrix multiplciatoin will be computed 
		using the underlying BLAS implementation. Unless the __validate__ flag
		is set on the module level, no error-checking is done. This function may
		be faster that CeLinalg.cdot for large matrices
	"""
	
	if __validate__:
		debug = np.dot(A,B)
		assert np.all(debug==C), "ERR: failed to correctly multiply matrices :"+ Errors.state(A,B)

	gemm = get_blas_funcs("gemm",[A,B])
	return gemm(1,A,B)

	
	
if __name__ == '__main__':
	# a = np.array([[2,1,5,.1],[5,3,9,8],[2,6,4,-4],[.1,3,2,5]]).astype(float)
	# b = np.array([[7,3,1,9],[3,3,2,1],[8,8,4,7],[4,0,0,5]]).astype(float)
	
	import numpy.random as rand
	
	MODE = 'ACCURACY'
	a = np.zeros((50,785))
	a[:,0] = 1
	print(a)
	b = rand.random((785,100))

	if MODE == 'DISTRO':
		
		for i in range(100):
			dot(a,b)
		
		__POOL__.display()
	elif MODE == 'ACCURACY':
		for p in range(2):
			print(p)
			# print('starting')
			a = rand.random((50,785))
			b = rand.random((785,100))
			x = dot(a,b)
			# print(x)
			# print(np.dot(a,b))
			
			print()
			# print(x==np.dot(a,b))
			assert np.all(x==np.dot(a,b))
			# print('stopping')
	
	
	# import numpy.random as random
	# a = random.random((5,5))
	# b = random.random((5,5)).astype(float)
	# print(dot(a,b)==a.dot(b))
	# print(a.dtype==float)