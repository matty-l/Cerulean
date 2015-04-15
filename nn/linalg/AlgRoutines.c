/**
	This file contains the subroutines used by Linalg.c
	
	Author: Matthew Levine
	Date: 04/14/2015
**/

#include <C:\Users\Dev\Desktop\Cerebro2\nn\linalg\\Linalg.h>

/* Global variables */
double* data_1_g = NULL;
double* data_2_g = NULL;
double* data_3_g = NULL;
int colsA_g = 0;
int colsB_g = 0;
int rowsA_g = 0;
int num_threads_g = 1;
int blocks_g = 1;

/* Adjusts the global parameters */
void set_global_multiplication_parameters( double* data_1, 
	double* data_2, double *data_3, int colsA, int colsB, int rowsA, 
	int num_threads, int blocks ){
		
	// if (data_1_g)
		// free(data_1_g);
	
		
	data_1_g = data_1;
	data_2_g = data_2;
	data_3_g = data_3;
	colsA_g = colsA;
	colsB_g = colsB;
	rowsA_g = rowsA;
	num_threads_g = num_threads;
	blocks_g = blocks;
}


/** This function nultiplies a partition of a matrix
*/
void *mlt_part_blocked(void *ptr){
	if (!data_1_g || !data_2_g || !data_3_g )
		printf("Warning: attempting to multiply undefined data\n");

	int part = *((int *)ptr);
	int i,j,k;
	int i0,j0,k0; /* For partitioning */
		
	int blocks = blocks_g;
	
	assert(num_threads_g > 0);

	const int start_row = rowsA_g * part / num_threads_g;
	const int stop_row  = rowsA_g * (part+1) / num_threads_g;
	
	assert(stop_row > start_row);
	
	for (i0 = start_row; i0 < stop_row; i0 += blocks ){
		for (j0 = 0; j0 < colsB_g; j0+=blocks){
				
			const int imax = min(i0+blocks,stop_row);
			
			for (i = i0; i < imax; i++){
			
				const int jmax = min(j0+blocks,colsB_g);
				for (j = j0; j < jmax; j++){
					
					const int row = (colsB_g) * i;
					
					double sum = 0;
					for (k0 = 0; k0 < colsA_g; k0 += blocks){
					
						const int kmax = min(k0+blocks,colsA_g);						
						for (k = k0; k < kmax; k++){
							sum += data_1_g[colsA_g*i+k] * data_2_g[k*(colsB_g)+j];
						}
						data_3_g[ row + j ] = sum;		
					}
					
				}
			}
		}
	}
	
	return NULL;	
}

/** This function nultiplies a partition of a matrix
*/
void *mlt_part(void *ptr){
	int part = *((int *)ptr);
	int i,j,k;
	
	
	assert(num_threads_g > 0);

	int start_row = rowsA_g * part / num_threads_g;
	int stop_row  = rowsA_g * (part+1) / num_threads_g;
	
	assert(stop_row > start_row);
					
	for (j = 0; j < colsB_g; j++)
		for (i = start_row; i < stop_row; i++){
		
			const int tmp = (colsB_g) * i;
			double sum = 0;
			for (k = 0; k < colsA_g; k++){
				sum += data_1_g[colsA_g*i+k] * data_2_g[k*(colsB_g)+j];
			}
			data_3_g[ tmp + j ] = sum;		
		}
		
	return NULL;
}


/* For testing the C algorithms independently of the Python interpreter 
	enviornment, or for compiling these algorthms to use with a c profiler
*/
int main ( int argc, char *argv[] ){
	int N = 100;
	int M = 1;
	int B = 5;
	
	if (argc < 2){
		printf("Usage: \" gcc AlgRoutines N M \" \n");
		N = atoi(argv[1]);
		assert(N>0);
	}
	
	
	if (argc > 2){
		M = atoi(argv[2]);
		assert(M>0);
	}
	
	if (argc > 3){
		B = atoi(argv[3]);
		assert(B>0);
	}
	
	printf("Arguments decided are N=%d, M=%d, B=%d\n",N,M,B);
	
	printf("Constructing 3 matrices of total entry %d, dimension %d\n",N*N,N);
	const int size = sizeof(double) * N * N;
	double *data1 = malloc(size);
	double *data2 = malloc(size);
	double *data3 = malloc(size);
	if (!data1 || !data2 || !data3)
		printf("Failed to allocate data for multiplication\n");
	
	srand48(5);//time(NULL));
	
	printf("Initializing matrix data\n");
	int i,j;
	for (i = 0; i < N*N; i++){
		    data1[i] = drand48();
			data2[i] = drand48();
	}

	printf("Setting parameters\n");
	set_global_multiplication_parameters( data1, data2, data3, N, N, N, 1, B );
	
	int *tid = malloc(sizeof(int));
	*tid = 0;

	struct timespec start, finish;
	double elapsed;	
	clock_gettime(CLOCK_MONOTONIC, &start);
	
	printf("Multiplying...\n");
	for (j = 0; j < M; j++) mlt_part_blocked((void*)tid);

	clock_gettime(CLOCK_MONOTONIC, &finish);
	elapsed = (finish.tv_sec - start.tv_sec);
	elapsed += (finish.tv_nsec - start.tv_nsec) / 1000000000.0;
	
	printf("Elapsed time: %f Time Per Call %f\n\n",elapsed,elapsed/M);

		
	if (N < 10){
		for (i = 0; i < N; i++){
			for (j = 0; j < N; j++){
				printf("%f ",data3[i*N+j]);
			}
			printf("\n");
		}
	}
	
	/* Ceremonial memory management */
	free(tid);
	free(data1); free(data2); free(data3);
	
	return 0;
}