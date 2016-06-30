'''
Alex Arsenovic, Michael Eller, Noah Sauber
UVA THZ CAI
'''

import skrf as rf
from skrf import micron
import os, os.path
import instruments as dev
from PIL import Image, ImageDraw
import subprocess
import math
import numpy as np
import time
import matplotlib.pyplot as plt
from skrf.media import Freespace
from pylab import *

import projector
import decoder
import structure

class CAI(object):
	def __init__(self, base_dir = os.getcwd(), start = False, resolution = 10, lia = 1):
		'''
		A class to perform data collection and image creation

		@Params
		dimension: resolution of the mask
		resolution = 2^dimension (not resolution of schottky pic, resolution of the resulting pixelated image)
		(dimension = 1 -> 2x2, dimension = 2 -> 4x4)

		canvasSize: size of the mask image
		'''
		self.base_dir = base_dir
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

		#else:
			#print "NOTE: GPIB instuments have not been initialized."

		if not os.path.exists('Data'):
			os.mkdir('Data')
			os.chdir('Data')
			os.mkdir('hadamard')
			os.mkdir('raster')
			os.mkdir('bar')
			os.mkdir('walsh')
			os.mkdir('random')
			os.chdir('..')

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
		plt.colorbar().set_label(label = 'Volts',rotation = 'horizontal')
		plt.ylabel('Y (' + str(step) + ' mm)')
		plt.xlabel('X (' + str(step) + ' mm)')
		grid(0)
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

	#routine to take hadamard image
	def hadamard_image(self, hadamard, name, delay = 1, measurements = 1, averaging_delay = 0, duty_cycle = False):
		#take_data = True, duty_cycle = False, cal = None, averaging = True, caching = True, f = '634ghz', attr = 's_db'
		'''
		TO DO: implement modifiable duty_cyce
		NOTE: might have to change order of slides for variant = 'both' --> currently: all primary then all inverse
		future possibly: primary inverse primary inverse primary etc...
		'''
		data = structure.image_data(hadamard, name)

		#if take_data:
		ppt = projector.PPT(hadamard)
		ppt.start_pres()
		time.sleep(5)

		start_time = 0
		elapsed_time = 0

		#take primary data
		if hadamard.variant == 'primary' or hadmard.variant == 'both':
			for x in range (0, hadamard.size):
				start_time = time.time()
				ppt.show_slide(x + 2)
				time.sleep(delay)
				measurement_list = []
				for y in range (0, measurements):
					measurement_list.append(self.zva.get_network(name = 'measurement_' + str(y) + '.s1p'))
					time.sleep(averaging_delay)
				data.add_primary_data(decoder.mask2hex(hadamard.primary_masks[x]), measurement_list)
				elapsed_time = time.time() - start_time
				if duty_cycle:
					ppt.first_slide()
					time.sleep(elapsed_time)

		#take inverse data
		if hadamard.variant == 'inverse' or hadamard.variant == 'both':
			for x in range (0, hadamard.size):
				start_time = time.time()
				ppt.show_slide(hadamard.size + x + 2)
				time.sleep(delay)
				measurement_list = []
				for y in range (0, measurements):
					measurement_list.append(self.zva.get_network(name = 'measurement_' + str(y) + '.s1p'))
					time.sleep(averaging_delay)
				data.add_inverse_data(decoder.mask2hex(hadamard.inverse_masks[x]), measurement_list)
				elapsed_time = time.time() - start_time
				if duty_cycle:
					ppt.first_slide()
					time.sleep(elapsed_time)

		projector.kill_pptx()

		'''
		TO DO: implement variant options in decoder
		'''
		return data

	def take_hadamard_cal_set(self, hadamard, delay = 0, duty_cycle = False):
		cals = structure.cal_set(hadamard)

		#if take_data:
		ppt = projector.PPT(hadamard)
		ppt.start_pres()
		raw_input('Press Enter to Continue...')

		start_time = 0
		elapsed_time = 0

		#take primary data
		if hadamard.variant == 'primary' or hadmard.variant == 'both':
			for x in range (0, hadamard.size):
				start_time = time.time()
				ppt.show_slide(x + 2)
				time.sleep(delay)
				cals.data['primary'][decoder.mask2hex(hadamard.primary_masks[x])] = self.take_simple_cal()
				elapsed_time = time.time() - start_time
				if duty_cycle:
					ppt.first_slide()
					time.sleep(elapsed_time)

		#take inverse data
		if hadamard.variant == 'inverse' or hadamard.variant == 'both':
			for x in range (0, hadamard.size):
				start_time = time.time()
				ppt.show_slide(hadamard.size + x + 2)
				time.sleep(delay)
				cals.data['primary'][mask2hex(hadamard.inverse_masks[x])] = self.take_simple_cal()
				elapsed_time = time.time() - start_time
				if duty_cycle:
					ppt.first_slide()
					time.sleep(elapsed_time)

		projector.kill_pptx()

		return cals


	def take_bar_image(self):
		raise NotImplementedError

	def take_raster_image(self):
		raise NotImplementedError

	def walsh_image(self, walsh, name, delay = 1, measurements = 1, averaging_delay = 0):
		'''
		TO DO: implement variant and duty cycle stuff
		'''
		data = structure.image_data(walsh, name)
		ppt = projector.PPT(walsh)
		ppt.start_pres()
		time.sleep(5)

		for x in range (0, walsh.size):
			ppt.show_slide(x + 2)
			time.sleep(delay)
			measurement_list = []
			for y in range (0, measurements):
				measurement_list.append(self.zva.get_network(name = 'measurement_' + str(y) + '.s1p'))
				time.sleep(averaging_delay)
			data.add_primary_data(decoder.mask2hex(walsh.primary_masks[x]), measurement_list)

			projector.kill_pptx()

		return data

	def take_walsh_cal_set(self, walsh, delay = 0):
		'''
		TO DO: implement duty cycle stuff and variant stuff
		'''
		cals = structure.cal_set(walsh)

		ppt = projector.PPT(walsh)
		ppt.start_pres()
		time.sleep(5)

		for x in range (0, walsh.size):
			ppt.show_slide(x + 2)
			time.sleep(delay)
			cals.data['primary'][decoder.mask2hex(walsh.primary_masks[x])] = self.take_simple_cal()

		projector.kill_pptx()

		return cals

	def take_random_image(self):
		raise NotImplementedError

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