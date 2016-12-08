"""write_stl.py
Rex Garland <rgarland@stanford.edu>
ENGR 241, Fall 2016
"""

import numpy as np
import sys

def write_stl(function, filename):
	with open(filename, 'w') as f:
		f.write("solid 1mm\n") # choose unit
		f.write(function())
		f.write("endsolid 1mm\n")

def well_test():
	"""Write stl model text for testing various well dimensions.
	|w| well width
	|d| well depth"""
	text = ''
	widths = [0.05, 0.1, 0.2, 0.4]
	depths = [0.2, 0.4, 0.8]
	min_x = 0; max_x = 0; min_y = 0; max_y = 0
	total_width = 1.0
	height = 1
	offset = {}
	for i in range(len(widths)):
		w = widths[i]
		t = (total_width-w)/2
		offset['x'] = i*total_width
		for j in range(len(depths)):
			d = depths[j]
			print w, d
			offset['y'] = j*total_width
			well = {}
			well['corner'] = (offset['x'],offset['y'],0)
			well['w'] = w; well['t'] = t; well['h'] = height; well['d'] = d
			text += write_well(well)
			max_x = max(max_x, offset['x']+total_width)
			max_y = max(max_y, offset['y']+total_width)
	base = {}
	base['min_x'] = min_x; base['max_x'] = max_x; base['min_y'] = min_y; base['max_y'] = max_y
	base['height'] = 0.5; base['buffer'] = 3
	text += write_base(base)
	return text

def write_well(data):
	"""Write stl text for a well.
	|w| width
	|t| wall thickness
	|h| total height
	|d| well depth
	|data| has keys |corner|, |w|, |t|, |h|, |d|"""
	text = ''
	corner, w, t, h, d = data['corner'], data['w'], data['t'], data['h'], data['d']
	prism = {}
	prism['corner'] = corner
	prism['v1'] = (t+w, 0, 0); prism['v2'] = (0, t, 0); prism['v3'] = (0, 0, h)
	text += write_prism(prism)
	prism['corner'] = (corner[0]+t+w, corner[1], corner[2])
	prism['v1'] = (t, 0, 0); prism['v2'] = (0, t+w, 0); prism['v3'] = (0, 0, h)
	text += write_prism(prism)
	prism['corner'] = (corner[0]+2*t+w, corner[1]+t+w, corner[2])
	prism['v1'] = (0, t, 0); prism['v2'] = (-t-w, 0, 0); prism['v3'] = (0, 0, h)
	text += write_prism(prism)
	prism['corner'] = (corner[0]+t, corner[1]+2*t+w, corner[2])
	prism['v1'] = (-t, 0, 0); prism['v2'] = (0, -t-w, 0); prism['v3'] = (0, 0, h)
	text += write_prism(prism)
	prism['corner'] = (corner[0]+t, corner[1]+t, corner[2])
	prism['v1'] = (w, 0, 0); prism['v2'] = (0, w, 0); prism['v3'] = (0, 0, h-d)
	text += write_prism(prism)
	return text

def bridge_test():
	"""Write stl text for creating bridges of varying length / thickness.
	|t| thickness of prism bridge
	|l| length of prism bridge"""
	text = ''
	thicknesses = [0.05, 0.1, 0.2]
	lengths = [0.4, 0.8, 1.6, 3.2]
	num_bridges = 3
	bridge_height = 0.5
	bridge_base_width = 0.2
	bridge_base_length = 1.6
	buff = 0
	max_x = 0; min_x = 0
	max_y = 0; min_y = 0
	for i in range(len(lengths)):
		l = lengths[i]
		offset = {}
		offset['x'] = max_x+buff
		for j in range(len(thicknesses)):
			t = thicknesses[j]
			print l, t
			offset['y'] = j*(bridge_base_length+buff)
			bridge_base = {}
			bridge_base['corner'] = (offset['x'], offset['y'], 0)
			bridge_base['v1'] = (bridge_base_width, 0, 0)
			bridge_base['v2'] = (0, bridge_base_length, 0)
			bridge_base['v3'] = (0, 0, bridge_height+t)
			text += write_prism(bridge_base)
			bridge_base['corner'] = (offset['x']+bridge_base_width+l, offset['y'], 0)
			bridge_base['v1'] = (bridge_base_width, 0, 0)
			bridge_base['v2'] = (0, bridge_base_length, 0)
			bridge_base['v3'] = (0, 0, bridge_height+t)
			text += write_prism(bridge_base)
			for k in range(num_bridges):
				bridge = {}
				bridge['corner'] = (offset['x']+bridge_base_width, offset['y']+(k+1)*bridge_base_length/(num_bridges+1)-t/2, bridge_height)
				bridge['v1'] = (l, 0, 0)
				bridge['v2'] = (0, t, 0)
				bridge['v3'] = (0, 0, t)
				text += write_prism(bridge)
			max_x = max(max_x, offset['x']+2*bridge_base_width+l)
			max_y = max(max_y, offset['y']+bridge_base_length)
	base = {}
	base['min_x'] = min_x; base['max_x'] = max_x; base['min_y'] = min_y; base['max_y'] = max_y
	base['height'] = 0.5
	base['buffer'] = 3
	text += write_base(base)
	return text

def aspect_ratio_test():
	"""Write characterization file for testing 3d printer for various aspect ratios."""
	text = ''
	smallest_dimension = 0.1
	sizes = 2**np.arange(4)*smallest_dimension # sizes to permute (factors of 2)
	e1 = np.array([1,0,0]); e2 = np.array([0,1,0]); e3 = np.array([0,0,1])
	num_permutations = (len(sizes)*(len(sizes)+1)/2)*len(sizes) # don't double-count x,y and y,x
	num_x = int(np.sqrt(num_permutations)) # layout blocks in approximate square
	buffer_distance = max(sizes)*0.3 # minimum distance between blocks
	offset = (max(sizes)+buffer_distance)
	count = 0
	max_x = 0; max_y = 0
	# place all permutations of the above sizes
	for i in reversed([(sizes[i],sizes[j],sizes[k]) for i in range(len(sizes)) for j in range(i,len(sizes)) for k in range(len(sizes))]):
		print ' '.join([str(a) for a in i])
	for permutation in [(sizes[i],sizes[j],sizes[k]) for i in range(len(sizes)) for j in range(i,len(sizes)) for k in range(len(sizes))]:
		l, w, h = permutation
		x = (count-num_x*(count//num_x))*offset; y = (count//num_x)*offset
		position = (x,y,0)
		data = {'corner': position, 'v1': l*e1, 'v2': w*e2, 'v3': h*e3}
		text += write_prism(data)
		max_x = max(max_x, x+l); max_y = max(max_y, y+w)
		count += 1
	# create base
	percent_over = 1 # this percentage of length and width will be added to the base
	length = max_x*(1+percent_over); width = max_y*(1+percent_over)
	length = max(length, 10); width = max(width, 10) # at least 1cm in order to grab
	height = 0.5 # 0.5mm base (good standard to keep)
	center = np.array([max_x, max_y, 0], np.float)/2
	corner = center-np.array([length/2., width/2., height])
	data = {'corner': corner, 'v1': length*e1, 'v2': width*e2, 'v3': height*e3}
	text += write_prism(data)
	return text

def pillar_test():
	"""Write characterization file for testing 3d printer for various pillar dimensions (width, buffer, heigh).
	This file creates blocks of pillars (5x5 set) and spaces them out along a print"""
	text = ''
	n = 5
	permutations = [(w,r) for w in [0.1, 0.2, 0.4] for r in [2, 4]]
	max_x = 0; max_y = 0; min_x = 0; min_y = 0;
	for w, r in permutations:
		h = w*r
		buff = w
		print w, h
		offset = (max_x+buff, 0)
		for i in range(n):
			for j in range(n):
				data = {}
				data['corner'] = (offset[0]+i*(w+buff), offset[1]+j*(w+buff), 0)
				data['v1'] = (w,0,0); data['v2'] = (0,w,0); data['v3'] = (0,0,h)
				text += write_prism(data)
		max_x = max(max_x, offset[0]+n*(w+buff))
		min_x = min(min_x, offset[0])
		max_y = max(max_y, offset[1]+n*(w+buff))
		min_y = min(min_y, offset[1])
	# create base
	base_data = {}
	base_data['min_x'] = min_x; base_data['max_x'] = max_x; base_data['min_y'] = min_y; base_data['max_y'] = max_y
	base_data['height'] = 0.5
	base_data['buffer'] = 3
	text += write_base(base_data)
	return text

def write_base(data):
	"""Write stl text for a base.
	|data| has keys |min_x|, |min_y|, |max_x|, |max_y|, |height|, |buffer|"""
	prism_data = {}
	prism_data['corner'] = (data['min_x']-data['buffer'], data['min_y']-data['buffer'], -data['height'])
	prism_data['v1'] = (data['max_x']-data['min_x']+2*data['buffer'], 0, 0)
	prism_data['v2'] = (0, data['max_y']-data['min_y']+2*data['buffer'], 0)
	prism_data['v3'] = (0,0,data['height'])
	return write_prism(prism_data)

def write_cube(data):
	"""Write stl text for a cube using data on a center (on bottom face) and height."""
	text = ''
	center = np.array(data['center'])
	height = data['height']
	e1 = np.array([1,0,0]); e2 = np.array([0,1,0]); e3 = np.array([0,0,1])
	data = {'corner': center-height/2*(e1+e2), 'v1': height*e1, 'v2': height*e2, 'v3': height*e3}
	text = write_prism(data)
	return text

def write_prism(data):
	"""Write stl text for a prism using data on a corner (on bottom face), length, width, and height vectors.
	|data| has keys |corner|, |v1|, |v2|, |v3|.
	v1, v2, and v3 must be ordered according to the right hand rule."""
	text = ''
	corner = np.array(data['corner'])
	v1 = np.array(data['v1']); v2 = np.array(data['v2']); v3 = np.array(data['v3']) # should be ordered using right hand rule
	square_data = {'corner': corner, 'v1': v2, 'v2': v1}
	text += write_plg(square_data)
	square_data = {'corner': corner, 'v1': v1, 'v2': v3}
	text += write_plg(square_data)
	square_data = {'corner': corner, 'v1': v3, 'v2': v2}
	text += write_plg(square_data)
	square_data = {'corner': corner+v1+v2+v3, 'v1': -v1, 'v2': -v2}
	text += write_plg(square_data)
	square_data = {'corner': corner+v1+v2+v3, 'v1': -v3, 'v2': -v1}
	text += write_plg(square_data)
	square_data = {'corner': corner+v1+v2+v3, 'v1': -v2, 'v2': -v3}
	text += write_plg(square_data)
	return text

def write_plg(data):
	"""Write stl text for making a parallelogram using a corner and two vectors for data."""
	text = ''
	vertex1 = np.array(data['corner'])
	v1 = np.array(data['v1']); v2 = np.array(data['v2'])
	vertex2 = vertex1+v1;
	vertex3 = vertex1+v2;
	vertex4 = vertex1+v2+v1;
	vertex5 = vertex4-v1;
	vertex6 = vertex4-v2;
	normal = np.cross(v1, v2); normal = normal/np.linalg.norm(normal)
	text += 'facet normal {} {} {}\n'.format(*normal)
	text += '  outer loop\n'
	text += 'vertex {} {} {}\n'.format(*vertex1)
	text += 'vertex {} {} {}\n'.format(*vertex2)
	text += 'vertex {} {} {}\n'.format(*vertex3)
	text += '  endloop\n'
	text += 'endfacet\n'
	text += 'facet normal {} {} {}\n'.format(*normal)
	text += '  outer loop\n'
	text += 'vertex {} {} {}\n'.format(*vertex4)
	text += 'vertex {} {} {}\n'.format(*vertex5)
	text += 'vertex {} {} {}\n'.format(*vertex6)
	text += '  endloop\n'
	text += 'endfacet\n'
	return text

if __name__=='__main__':
	"""Usage: python write_stl.py [filename]"""
	filename = sys.argv[1]
	# insert appropriate function for creating corresponding stl model
	write_stl(pillar_test, filename)





