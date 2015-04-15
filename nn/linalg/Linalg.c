/*
	This file contains linalg functions
	
	Author: Matthew Levine
	Date: 10/2/2014
*/

#include <C:\Users\Dev\Desktop\Cerebro2\nn\linalg\\Linalg.h>
#include <Python.h>
#include "C:\Python34/Lib/site-packages/numpy/core/include/numpy/arrayobject.h"

/* Multiplies two matrices; expects to be called from a Python interpreter */
static PyObject* multiply(PyObject* self, PyObject* args);

 
/* -- Boring Cython Stuff -- */
PyDoc_STRVAR(CaLalg_Documentation,
	" This is a C linalg package for fast linalg operations " );
	
static PyMethodDef CaLalg_Methods[] = {
	{"multiply",multiply,METH_VARARGS,
		"Multiples two matrices and puts the output into the third\
		\
		This is supposed to be optimized matrix multiplication,\
		with the dream to beat numpy.\
		\
		Handles 2d arrays only. Accepts three arrays as input, one must be\
		the output array. The other two must be compatible for matrix multiplication.\
		Returns 0 if it detects an error. Does minimal error detection.\
		\
		Variable type should be float. This is not typically default type\
	"},
	{ NULL, NULL, 0, NULL }
};

static struct PyModuleDef CaLalg_Module = {
	PyModuleDef_HEAD_INIT,
	"CaLalg",
	CaLalg_Documentation,
	1,
	CaLalg_Methods,
	NULL,NULL,NULL,NULL,NULL
};

/* -- End boring Cython stuff -- */

/* Local prototypes */
void *dot(void *ptr);
/* -- End local prototypes */

/** This executes when the module is loaded */
PyMODINIT_FUNC
PyInit_CaLalg(void)
{
	
	return PyModule_Create(&CaLalg_Module);
}


	
// char *ThreadInitException = 

/** Optimized matrix multiplication with the dream to beat numpy

  * Handles 2d arrays only. Accepts three arrays as input, one must be
  * the output array. The other two must be compatible for matrix multiplication.
  *
  * Returns 0 if it detects an error. Does minimal error detection.
  *
  * Variable type should be float. This is not typically default type
*/
static PyObject* multiply(PyObject* self, PyObject *args){
	
	/* Get variables */
	int rowsA,colsA,colsB; 
	int i,j,k;
	int blocks;
	PyArrayObject * nparray1;
	PyArrayObject * nparray2;
	PyArrayObject * nparray3;
	int num_threads;
	
	if (!PyArg_ParseTuple(args,"OOOii",&nparray1,&nparray2,&nparray3,
			&num_threads,&blocks))
		return Py_BuildValue("i",1);
	
	
	double* data_1 = (double*) nparray1->data;
	double* data_2 = (double*) nparray2->data;
	double* data_3 = (double*) nparray3->data;
	
	rowsA = nparray1->dimensions[0];
	colsA = nparray1->dimensions[1];
	if (colsA != nparray2->dimensions[0]) 
		return Py_BuildValue("i",2);
	colsB = nparray2->dimensions[1];
		
	if (nparray3->dimensions[0] != rowsA || nparray3->dimensions[1] != colsB){
		return Py_BuildValue("i",3);
	}
	/* -- We now have the variables */
	
	/* Set up threading */
	pthread_t* threads = NULL;
	const int use_mult = num_threads > 1;
		
		if (use_mult){
			threads = malloc(sizeof(pthread_t) * num_threads);
		if (!threads)
			printf("Warning: Memory failure on thread allocation\n");
		
			
		set_global_multiplication_parameters( data_1, data_2, data_3, colsA, 
			colsB, rowsA, num_threads, blocks );
	}
	/* -- Threading is ready */
		
	/* If we have one thread, do things simply */
	if (!use_mult){
		for (i = 0; i < rowsA; i++){
			const int tmp = (colsB) * i;
			for (j = 0; j < colsB; j++){				
				double sum = 0;
				for (k = 0; k < colsA; k++){
					sum += data_1[colsA*i+k] * data_2[k*(colsB)+j];
				}
				data_3[ tmp + j ] = sum;
				
			}
		}
	}else{
		/* Perform threaded multiplication */
		int* thread_count = malloc(sizeof(int)*num_threads);
		if (!thread_count)
			printf("Warning: memory failure on thread count allocation\n");
		
		if (!thread_count){
			printf("Major memory allocation problems occured in Linalg.c\n");
		}
		for (i = 0; i < num_threads; i++)
			thread_count[i] = i;
		void* jfill; /* For joining threads */
		
		
		for (i = 0; i < num_threads; i++){	
			if (blocks == 1){
				if (pthread_create(&threads[i],NULL,mlt_part,&thread_count[i])){
					printf("Failed to create thread, humanity's fate grim\n");
				}
			}
			else
				if (pthread_create(&threads[i],NULL,mlt_part_blocked,&thread_count[i]))
					printf("Failed to create thread, humanity's fate grim\n");
		}
		for (i = 0; i < num_threads; i++){
			if (pthread_join(threads[i],jfill)) 
				printf("Thread %d would not wait, high casualties expected\n",i);									
		}
		
		if (thread_count)
			free(thread_count);
	}
	
	if (threads) free(threads);
	
	
	return Py_BuildValue("i",0); 
}
