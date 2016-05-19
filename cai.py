#Michael Eller
#Noah Sauber
#9 July 2015

import skrf as rf
from skrf import micron
import os, os.path
import instruments as dev
import matrixDecoder as mm
from PIL import Image, ImageDraw
import subprocess
import math
import numpy as np
import time as time
import pylab
import matplotlib.pyplot as plt
from skrf.media import Freespace

class CAI(object):
	def __init__(self, dimension = 4, canvasSize = 1024, start = False, resolution = 10, lia = 1):
		'''
		A class to perform data collection and image creation

		@Params
		dimension: resolution of the mask
		resolution = 2^dimension (not resolution of schottky pic, resolution of the resulting pixelated image)
		(dimension = 1 -> 2x2, dimension = 2 -> 4x4)

		canvasSize: size of the mask image
		'''
		self.dimension = dimension
		self.canvasSize = canvasSize
		self.matrixList = createH(self.dimension,'111-', [])
		self.xpos = 0
		self.resolution = resolution
		self.schottky = [[0 for x in range(self.resolution)] for x in range(self.resolution)]
		if start:
			self.esp = dev.ESP()
			self.zva = dev.ZVA()
			self.mm = dev.KEITHLEY()
			if lia:
				self.lia = dev.LIASR530()
			else:
				self.lia = dev.LIA5209()

		else:
			print "NOTE: GPIB instuments have not been initialized."

	def start_esp(self):
		self.esp = dev.ESP()

	def start_zva(self):
		self.zva = dev.ZVA()

	def start_lia(self, lia = 1):
		if lia:
			self.lia = dev.LIASR530()
		else:
			self.lia = dev.LIA5209()

	def start_mm(self):
		self.mm = dev.KEITHLEY()

	def start_all(self, lia = 1):
		self.esp = dev.ESP()
		self.zva = dev.ZVA()
		self.mm = dev.KEITHLEY()
		if lia:
			self.lia = dev.LIASR530()
		else:
			self.lia = dev.LIA5209()


	def writeHText(self, o = '111-'):
		f = open("matrices_rec.txt", "w")
		for matrix in self.matrixList:
			f.write(matrix + '\n')
		f.close()
		f = open("matrices.txt", "w")
		temp = recursion_fix(self.dimension, self.matrixList)
		for matrix in temp:
			f.write(matrix + '\n')
		f.close()

	def take_simple_cal(self, load = False):
		self.esp.position = 0
		time.sleep(1)
		'''
		get networks
		'''
		meas = {}
		for x in range(0,6):
			name = 'ds,' + str(x)
			self.esp.position = -0.04*x
			time.sleep(1)
			n = self.zva.get_network(name = name)
			meas[name] = n
		'''
		get perfect load
		'''
		if load:
			name = 'pl'
			self.esp.position = 0
			time.sleep(8)
			n = self.zva.get_network(name = name)
			meas[name] = n
		delta = 40
		freq = meas.values()[0].frequency
		air = Freespace(frequency = freq, z0=50)
		si = Freespace(frequency = freq , ep_r=11.7 , z0=50)
		if load:
			ideals = [ air.delay_short(k*delta,'um',name='ds,%i'%k) for k in range(6)] + [air.match(name = 'pl')]
		else:
			ideals = [ air.delay_short(k*delta,'um',name='ds,%i'%k) for k in range(6)] #**si.delay_short(350,'um')
		cal_q = rf.OnePort(measured = meas, ideals = ideals, sloppy_input=True, is_reciprocal=False)
		self.esp.position = 0
		cal_q.plot_caled_ntwks(ls='', marker='.')
		return cal_q

	def take_image(self):
		DIR = 'obj'
		os.makedirs(DIR)
		os.chdir(DIR)
		self.esp.position = 0
		white = (255, 255, 255)
		hlist = self.matrixList
		size = self.canvasSize
		for i in range(0, len(hlist)):
			image = Image.new("RGB", (size, size), white)
			draw = ImageDraw.Draw(image)
			matrix = hlist[i]
			#start drawing!
			drawH(matrix, size, 0, 0, 2, draw)
			#start collecting data!
			image.save("mask.png")
			time.sleep(0.5)
			del image
			os.startfile('mask.png')
			time.sleep(2)
			#create files and save data!
			os.makedirs(str(i))
			os.chdir(str(i))
			self.zva.write_data('object')
			os.chdir("..")
			os.system("taskkill /im microsoft.photos.exe /f")
			time.sleep(1)
		os.chdir('..')

	def rename_folders(self, base_dir):
		matrixList = recursion_fix(self.dimension, self.matrixList)
		os.chdir(base_dir)
		for x in range(0, len(matrixList)):
			os.rename(str(x), str(int(format2bn(matrixList[x]), 2)))

	def set_dim(self, dim):
		self.dimension = dim
		self.matrixList = createH(dim,'111-', [])

	def set_canvas(self, c):
		self.canvasSize = c

	#resolution^2 is how many pixels
	#step size is how much the stage moves
	def schottky_pic(self, name, step = 5):
		self.esp.current_axis = 1
		self.esp.position = 0
		self.esp.current_axis = 2
		for x in range(0, self.resolution):
			self.esp.position = 0
			self.xpos = x
			print str(self.xpos + 1),
			self.esp.current_axis = 1
			self.esp.position += step
			time.sleep(2)
			for y in range (0, self.resolution):
				time.sleep(3)
				self.schottky[x][y] = self.lia.get_output()
				self.esp.current_axis = 2
				self.esp.position += step
		self.esp.position = 0
		self.esp.current_axis = 1
		self.esp.position = 0
		for x in range(0, self.resolution):
			for y in range(0, self.resolution):
				self.schottky[x][y] = float(self.schottky[x][y])
		self.write_scan_data(name, step)

	def write_scan_data(self, name, step):
		arr = np.array(self.schottky)
		CENTER_X = 0
		CENTER_Y = 0
		Y_R = 0
		X_R = 0
		check = False
		for x in range(0, self.resolution):
			for y in range(0, self.resolution):
				if self.schottky[x][y] >= np.amax(arr):
					CENTER_X = y
					CENTER_Y = x
				if ((np.amax(arr) * 0.34) < self.schottky[x][y] < (np.amax(arr) * 0.368)) and check == False:
					check = True
					Y_R = x
					X_R = y
		radius = math.sqrt(math.pow((X_R - CENTER_X), 2) + math.pow((Y_R - CENTER_Y), 2)) * step
		plotstr = ('Max: ' + str(np.amax(arr)) + ' V' + '\n' + 'Min: ' + str(np.amin(arr)) + 
			' V' + '\n' + 'Center: ' + '(' + str(CENTER_X) + ', ' + str(CENTER_Y) + ')' + '\n' + 
			'Est. Radius: ' + str(radius) + ' mm')
		plt.imshow(arr)
		plt.colorbar().set_label(label = 'Volts')
		plt.ylabel('Y (' + str(step) + ' mm)')
		plt.xlabel('X (' + str(step) + ' mm)')
		plt.title(name + '\n' + 'ZBD Voltage vs Position')
		plt.text(0, 0, plotstr, fontsize=10, verticalalignment='top',bbox=dict(facecolor='white', alpha=1))
		fig = plt.gcf()
		fig.gca().add_artist(plt.Circle((CENTER_X, CENTER_Y),radius * 2,color='w', alpha=1, fill = False))
		os.makedirs(name)
		os.chdir(name)
		f = open(name, "w")
		for x in range(0, self.resolution):
			f.write(str(x) + ':')
			for y in range(0, self.resolution):
				f.write(str(self.schottky[x][y]) + ', ')
			f.write('\n')
		f.close()
		plt.savefig(name)
		os.chdir('..')

	def schottky_pic_keithley(self, step = 5):
		self.esp.current_axis = 1
		self.esp.position = 0
		self.esp.current_axis = 2
		for x in range(0, self.resolution):
			self.esp.position = 0
			self.xpos = x
			print self.xpos
			self.esp.current_axis = 1
			self.esp.position += step
			for y in range (0, self.resolution):
				time.sleep(7)
				self.schottky[x][y] = self.mm.get_output()
				self.esp.current_axis = 2
				self.esp.position += step
		self.esp.position = 0
		self.esp.current_axis = 1
		self.esp.position = 0
		for x in range(0, self.resolution):
			for y in range(0, self.resolution):
				self.schottky[x][y] = float(self.schottky[x][y])
		arr = np.array(self.schottky)
		plt.imshow(arr)
		plt.colorbar()
		print self.schottky
		return self.schottky
    
	def get_Center(self):
		maximum = np.amax(self.schottky)
		for x in range (0, self.resolution):
			for y in range(0, self.resolution):
				if self.schottky[x][y] == maximum:
					return (x, y)

#simply turn -'s to 1's and vice versa
def inverse(s):
	string = ""
	for x in range(0, len(s)):
		if s[x] == '-':
			string += '1'
		else:
			string += '-'
	return string

#turn 1's to 0's and -'s to 1's
def format2bn(s):
	string = ""
	for x in range(0, len(s)):
		if s[x] == '1':
			string += '1'
		else:
			string += '0'
	return string

#take a list of 1 and - matrices and convert to binary
def list2bn(ml):
    bn = []
    for x in range(0,len(ml)):
        bn.append(cai.format2bn(ml[x]))
    return bn

#form the inverse matrix list
def inverse_ML(ml):
    inv = []
    for x in range(0,len(ml)):
        inv.append(cai.inverse(ml[x]))
    return inv

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
def createH(n, o, rlist):
	if n == 0:
		return rlist
	rlist.append(o)
	s = ""
	s += o
	s += o
	s += o
	s += inverse(o)
	rlist = createH(n - 1, s, rlist)
	o = shift(o, 1)
	rlist.append(o)
	s = ""
	s += o
	s += o
	s += o
	s += inverse(o)
	rlist = createH(n - 1, s, rlist)
	o = shift(o, 2)
	rlist.append(o)
	s = ""
	s += o
	s += o
	s += o
	s += inverse(o)
	rlist = createH(n - 1, s, rlist)
	o = shift(o, 3)
	rlist.append(o)
	s = ""
	s += o
	s += o
	s += o
	s += inverse(o)
	rlist = createH(n - 1, s, rlist)
	rlist.sort(key = len)
	#delete all combos that are not NxN (the smaller ones)
	counter = 0
	for x in range(0, len(rlist)):
		l = len(rlist[len(rlist) - 1])
		if len(rlist[x]) < l:
			counter += 1
	del rlist[0 : counter]
	return rlist

#draw the Hadamard Matrix recursively
#'matrix' is the string to be converted to an image
#'canvasSize' remains constant, 'x' and 'y' must be 0 to start
#'im' is the image draw object
#'n' must be 2 to start
def drawH(matrix, canvasSize, x, y, n, im):
	if len(matrix) == 4:
		for i in range(0,4):
			if matrix[i] == '1':
				im.rectangle(((x, y), (x + canvasSize / n, y + canvasSize / n)),
					fill = 'black', outline = 'black')
			if i == 1:
				x -= canvasSize / n
				y += canvasSize / n
			else:
				x += canvasSize / n
	else:
		s1 = matrix[0:len(matrix)/4]
		s2 = matrix[len(matrix) / 4 : len(matrix) / 2]
		s3 = matrix[len(matrix) / 2 : 3 * len(matrix) / 4]
		s4 = matrix[3 * len(matrix) / 4 : len(matrix)]
		drawH(s1, canvasSize, x, y, 2 * n, im)
		drawH(s2, canvasSize, x + canvasSize / n, y, 2 * n, im)
		drawH(s3, canvasSize, x, y + canvasSize / n, 2 * n, im)
		drawH(s4, canvasSize, x + canvasSize / n, y + canvasSize / n, 2 * n, im)

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

def redraw(name, step, resolution):
	os.chdir(name)
	schottky = [[0 for x in range(resolution)] for x in range(resolution)]
	f = open(name, 'r')
	for x in range(0, resolution):
		line = f.readline()
		line = line.split(':')[1]
		line = line.split(', ')
		for y in range(0, resolution):
			schottky[x][y] = float(line[y])
	f.close()
	arr = np.array(schottky)
	CENTER_X = 0
	CENTER_Y = 0
	Y_R = 0
	X_R = 0
	for x in range(0, resolution):
		for y in range(0, resolution):
			if schottky[x][y] >= np.amax(arr):
				CENTER_X = y
				CENTER_Y = x
	check = False
	xR = CENTER_Y
	yR = CENTER_X
	while(1):
		if yR >= resolution or xR >= resolution:
			print "Radius is out of scope"
			break
		if schottky[xR][yR] < (np.amax(arr) * 0.386):
			Y_R = xR
			X_R = yR
			break
		else:
			yR += 1
			xR += 1
	radius = math.sqrt(math.pow((X_R - CENTER_X), 2) + math.pow((Y_R - CENTER_Y), 2)) * step
	plotstr = ('Max: ' + str(np.amax(arr)) + ' V' + '\n' + 'Min: ' + str(np.amin(arr)) + 
		' V' + '\n' + 'Center: ' + '(' + str(CENTER_X) + ', ' + str(CENTER_Y) + ')' + '\n' + 
		'Est. Radius: ' + str(radius) + ' mm')
	plt.imshow(arr)
	plt.colorbar().set_label(label = 'Volts')
	plt.ylabel('Y (' + str(step) + ' mm)')
	plt.xlabel('X (' + str(step) + ' mm)')
	plt.title(name + '\n' + 'ZBD Voltage vs Position')
	plt.text(0, 0, plotstr, fontsize = 10, verticalalignment = 'top',bbox=dict(facecolor='white', alpha=1))
	fig = plt.gcf()
	fig.gca().add_artist(plt.Circle((CENTER_X, CENTER_Y),radius * 2, color='w', alpha=1, fill = False))
	plt.savefig(name)
	os.chdir('..')




	