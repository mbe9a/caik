'''
Alex Arsenovic, Michael Eller, Noah Sauber
UVA THZ CAI
'''

from PIL import Image, ImageDraw
import numpy as np


#class for creating hadamard encoded masks/images
class Hadamard(object):
	def __init__(self, rank, canvas_size = 1024, seed = '111-'):
		self.rank = rank
		self.canvas_size = canvas_size
		self.seed = seed

	@property
	def res(self):
		return 2**self.rank

	@property
	def raw_masks(self):
		return create_hadamard_masks(self.rank, self.seed, [])
	
	@property
	def primary_masks(self):
		binary = list2bin(self.rank, create_hadamard_masks(self.rank, self.seed, []))
		return np.array([[int(k) for k in matrix] for matrix in binary]).reshape((self.res**2,self.res**2))

	@property
	def inverse_masks(self):
		binary = list2bin(self.rank, inverse_mask_list(create_hadamard_masks(self.rank, self.seed, [])))
		return np.array([[int(k) for k in matrix] for matrix in binary]).reshape((self.res**2,self.res**2))
	
#draw the Hadamard Matrix recursively
#'matrix' is the string to be converted to an image
#'canvas_size' remains constant, 'x' and 'y' must be 0 to start
#'im' is the image draw object
#'n' must be 2 to start
def draw_hadamard_mask(matrix, canvas_size, x, y, n, im):
	if len(matrix) == 4:
		for i in range(0,4):
			if matrix[i] == '1':
				im.rectangle(((x, y), (x + canvas_size / n, y + canvas_size / n)),
					fill = 'black', outline = 'black')
			if i == 1:
				x -= canvas_size / n
				y += canvas_size / n
			else:
				x += canvas_size / n
	else:
		s1 = matrix[0:len(matrix)/4]
		s2 = matrix[len(matrix) / 4 : len(matrix) / 2]
		s3 = matrix[len(matrix) / 2 : 3 * len(matrix) / 4]
		s4 = matrix[3 * len(matrix) / 4 : len(matrix)]
		draw_hadamard_mask(s1, canvas_size, x, y, 2 * n, im)
		draw_hadamard_mask(s2, canvas_size, x + canvas_size / n, y, 2 * n, im)
		draw_hadamard_mask(s3, canvas_size, x, y + canvas_size / n, 2 * n, im)
		draw_hadamard_mask(s4, canvas_size, x + canvas_size / n, y + canvas_size / n, 2 * n, im)

#simply turn -'s to 1's and vice versa
def inverse(s):
	string = ""
	for x in range(0, len(s)):
		if s[x] == '-':
			string += '1'
		else:
			string += '-'
	return string

#form the inverse matrix list
def inverse_mask_list(ml):
	inv = []
	for x in range(0,len(ml)):
		inv.append(inverse(ml[x]))
	return inv

#turn 1's to 0's and -'s to 1's
def format2bin(s):
	string = ""
	for x in range(0, len(s)):
		if s[x] == '1':
			string += '1'
		else:
			string += '0'
	return string

#take a list of 1 and - matrices and convert to binary
def list2bin(dim, ml):
	new_list = recursion_fix(dim, ml)
	bn = []
	for x in range(0,len(ml)):
		bn.append(format2bin(new_list[x]))
	return bn



#rotating the h matrix to create the different combos 
#'s' is the string to shift, 'n' is how many times
def shift(s, n):
	temp = s
	for i in range(0, n):
		x = len(temp)/4
		l = len(temp)
		string = temp[l - x:] +temp[:l - x]
		temp = string
	return string

#create Hadamard matrices recursively
#'o' should be '111-' or some permutation on the initial call
#'n' is depth of recursion 0 = nothing 1 = 2x2 2 = 4x4 etc...
def create_hadamard_masks(n, o, rlist):
	if n == 0:
		return rlist
	rlist.append(o)
	s = ""
	s += o
	s += o
	s += o
	s += inverse(o)
	rlist = create_hadamard_masks(n - 1, s, rlist)
	o = shift(o, 1)
	rlist.append(o)
	s = ""
	s += o
	s += o
	s += o
	s += inverse(o)
	rlist = create_hadamard_masks(n - 1, s, rlist)
	o = shift(o, 2)
	rlist.append(o)
	s = ""
	s += o
	s += o
	s += o
	s += inverse(o)
	rlist = create_hadamard_masks(n - 1, s, rlist)
	o = shift(o, 3)
	rlist.append(o)
	s = ""
	s += o
	s += o
	s += o
	s += inverse(o)
	rlist = create_hadamard_masks(n - 1, s, rlist)
	rlist.sort(key = len)
	#delete all combos that are not NxN (the smaller ones)
	counter = 0
	for x in range(0, len(rlist)):
		l = len(rlist[len(rlist) - 1])
		if len(rlist[x]) < l:
			counter += 1
	del rlist[0 : counter]
	return rlist

def xcoor(n, li, x):
	if n == 0:
		return li
	else:
		dif = pow(2, x)
		temp = li[:]
		for i in range (0, len(li)):
			temp[i] = temp[i] + dif
		li = li + temp
		li = li + li
		return xcoor(n-1, li, x+1)

def ycoor(n, li, x):
	if n == 0:
		return li
	else:
		dif = pow(2, x)
		li = li + li
		temp = li[:]
		for i in range (0, len(li)):
			temp[i] = temp[i] + dif
		li = li + temp
		return ycoor(n-1, li, x+1)

def recursion_fix(dimension, matrixList):
		li = matrixList
		n = len(li) #Area and pixel count
		w = int(math.sqrt(n)) #Length and width
		b = dimension #Times of iteration
		xloc = xcoor(b, [0], 0)
		yloc = ycoor(b, [0], 0)
		final = []
		for i in range (0, n):
			combo = li[i]
			temp = [0]*n
			temp2 = ""
			for j in range(0, n):
				tot = xloc[j] + w*yloc[j]
				temp[tot] = combo[j]
			for j in range(0, len(temp)):    
				temp2 = temp2 + temp[j]
			final.append(temp2)
		return final