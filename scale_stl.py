"""scale_stl.py
Rex Garland <rgarland@stanford.edu>
ENGR 241, Fall 2016
"""

import numpy as np
import sys

def scale_file(filename, new_filename, factor):
	with open(filename,'r') as f:
		text = f.readlines()
	new_text = ''
	for line in text:
		if line.strip().split()[0]=='vertex':
			new_text += scale_line(line,factor)
		else:
			new_text += line
	with open(new_filename, 'w') as f:
		f.write(new_text)

def scale_line(line, factor):
	vertex = np.array([float(v) for v in line.strip().split()[1:]])
	new_vertex = vertex*factor
	new_line = ' '*4+'vertex'
	for v in new_vertex:
		new_line += ' '+str(v)
	return new_line+'\n'

if __name__=='__main__':
	"""Usage: python scale_stl.py [filename] [scale factor]"""
	"""Output: scaled version of [filename] in file [filname_scaled]"""
	filename = sys.argv[1]
	factor = float(sys.argv[2])
	new_filename = filename.split('.')[0]+'_scaled'+'.'+filename.split('.')[1]
	scale_file(filename, new_filename, factor)
