"""
	This file contains the class that inverts a neurnal network function
	
	Author: Matthew Levine
	Date: 03/15/2015
"""

from setup import NeuralNetwork as nnsetup
from train import train as nntrain,Opts
from feedforward import feedforward as nnff

from numpy import array, float, shape, zeros

from utils.utils import disp, get_command, get_flag_value
from utils.view_mats import view_mats

import reconstruction.nnvisualize as nnvis
import reconstruction.nnbuild_sequence 
from reconstruction.nnloadrecon import load_recon
from reconstruction.nnreconstruct import reconstruct
from reconstruction.nncreaterecon import create_and_save_recon


def test_sequence_build(filename,startindex):
	""" Tests the ability to build sequences """
	reconstruction.nnbuild_sequence.test_sequence(filename,startindex=startindex)
	
def main():
	import sys
	
	command = get_command("Flags:\n--make\n  (--batches [%d])\n  (--filename [%s])\n"+\
		"  (--downsample [%b])\n  (--epochs [%d])\n"+\
		"--show\n  (--filename [%s])\n  (--start [%d])\n--demo\n--view_mats")
	if command is None:
		disp("Terminating because don't recognize command")
		exit(3)
		
	filename = get_flag_value('filename',str,'test')
	numbatches = get_flag_value('batches',int,50)
	start = get_flag_value('start',int,0)
	downsample = get_flag_value('downsample',int,0)
	epochs = get_flag_value('epochs',int,10)
	
	if any((flag is None for flag in (filename,numbatches,start))):
		disp("Terminating due to misformatted flag")
		exit(1)
	
		
	if command == '--make':			
		create_and_save_recon(batches=numbatches,filename=filename,
			downsample=downsample,epochs=epochs)
	elif command == '--show':
		test_sequence_build(filename,start)
	elif command == '--demo':
		nnvis.testvis()
	elif command == '--view_mats':
		disp(view_mats())
	else:
		disp("Uknown command ",command)

	
if __name__ == '__main__':
	main()
	# test_sequence_build()
	# create_and_save_recon(downsample=0)
	
	# from reconstruction.nnvisualize import testvis as testvis
	# testvis()
