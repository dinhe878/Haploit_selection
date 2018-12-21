#!/opt/local/bin/python2.7
import sys
from math import log
import numpy as np
infile = open(sys.argv[1], 'r')
outfile = open(sys.argv[1]+".variables", "w")
outfile.write("Num_bp RS_Max RS_Min RS_Var\n")
for line in infile.readlines():
	line = line.rstrip()
	RS = line.split(" ")
	if len(RS) == 1:
		for i in range(2):
			outfile.write("0 100000 0 0\n")
	else:
		RS = map(int, RS)
		for i in range(2):
			outfile.write(str(len(RS)-1)+" "+str(max(RS))+" "+str(min(RS))+" "+str(np.var(RS))+"\n")
		
infile.close()
outfile.close()