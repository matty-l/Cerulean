/*
 * Include file for linalg operations. Does not include Python-specific
 * headers
 *
 * Author: Matthew Levine
 * Date: 10/02/2014
*/

#ifndef _LINALG_H_
#define _LINALG_H_

#define min(a,b) a<b?a:b


#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <pthread.h>
#include <assert.h>
#include <time.h>


/* Internally sets global variables within a module */
void set_global_multiplication_parameters( double* data_1, 
	double* data_2, double *data_3, int colsA, int colsB, int rowsA, 
	int num_threads, int blocks );
	
/* Performs matrix multiplication, given a thread id and using global data,
	with partitioned data
*/
void *mlt_part_blocked(void *ptr);


/* Performs matrix multiplication, given a thread id and using global data.
*/
void *mlt_part(void *ptr);


#endif