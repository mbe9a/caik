import numpy as np
from numpy.linalg import inv
import os
import cai
from matplotlib import pyplot as plt
import math

class matrixDec(object):
	def __init__(self, rank, freq, base_dir):
		self.rank = rank
		self.freq = freq
		self.base_dir = base_dir
		self.measured = self.make_d_matrix(self.get_re_list())
		self.imaginary = self.make_d_matrix(self.get_im_list())
		self.masks = self.make_m_matrix()
		self.mag = self.make_d_matrix(self.get_mag_list())
		self.image = self.compute_image()

	def get_mag_list(self):
		maglist = []
		rlist = self.measured
		ilist = self.imaginary
		for x in range(0, len(self.measured)):
			maglist.append(math.sqrt(math.pow(float(rlist[x]), 2) + math.pow(float(ilist[x]), 2)))
		return maglist

	def get_re_list(self):
		DIR = os.getcwd()
		folders = os.listdir(self.base_dir)
		os.chdir(self.base_dir)
		relist = []
		for x in range (0, len(folders)):
			os.chdir(folders[x])
			cwd = os.getcwd()
			relist.append(get_re(self.freq, cwd))
			os.chdir('..')
		os.chdir(DIR)
		return relist

	def get_im_list(self):
		DIR = os.getcwd()
		folders = os.listdir(self.base_dir)
		os.chdir(self.base_dir)
		imlist = []
		for x in range (0, len(folders)):
			cwd = os.getcwd()
			os.chdir(folders[x])
			imlist.append(get_im(self.freq, cwd))
			os.chdir('..')
		os.chdir(DIR)
		return imlist

	def make_d_matrix(self, mlist):
		array = []
		for matrix in mlist:
			temp = []
			temp.append(matrix)
			array.append(temp)
		return np.asarray(array)

	def make_m_matrix(self):
		temp = cai.recursion_fix(self.rank, cai.createH(self.rank, '111-', []))
		mlist = []
		for matrix in temp:
			mlist.append(matrix)
		rlist = []
		for matrix in mlist:
			ilist = []
			for x in range(0, len(matrix)):
				if matrix[x] == '1':
					ilist.append(float(matrix[x]))
				else:
					ilist.append(-1.)
			rlist.append(ilist)
		return rlist

	def compute_image(self):
		m1 = np.matrix(self.mag)
		m2 = inv(np.matrix(self.masks))
		return np.dot(m2, m1)

	def paint(self):
		image = np.reshape(self.image, (math.pow(2, self.rank), math.pow(2, self.rank)))
		plt.imshow(image, cmap='gray', interpolation='nearest', vmin=np.amin(self.image), vmax=np.amax(self.image))
		#plt.imshow(image, cmap='gray', interpolation='nearest', vmin = 0.20932635, vmax = 0.24861209)
		plt.show()



def get_re(freq, base_dir):
	DIR = os.getcwd()
	os.chdir(base_dir)
	f = open('object corrected.s1p', 'r')
	line = f.readline()
	while True:
		if line[0:3] == str(freq)[0:3]:
			break
		line = f.readline()
	index = 0
	for c in range(0, len(line)):
		if line[c] == ' ':
			index = c
			break
	line = line[index + 1:]
	for c in range(0, len(line)):
		if line[c] == ' ':
			index = c
			break
	line = line[:index]
	return float(line)

def get_im(freq, base_dir):
	DIR = os.getcwd()
	#os.chdir(base_dir)
	#print base_dir
	f = open('object.s1p', 'r')
	line = f.readline()
	while True:
		if line[0:3] == str(freq)[0:3]:
			break
		line = f.readline()
	index = 0
	for c in range(0, len(line)):
		if line[c] == ' ':
			index = c
			break
	line = line[index + 1:]
	for c in range(0, len(line)):
		if line[c] == ' ':
			index = c
			break
	line = line[index + 1:]
	return float(line)