#Michael Eller
#Noah Sauber
#9 July 2015

import visa
from skrf.vi.vna import ZVA40
from skrf.vi.stages import ESP300
import numpy
import time as time

class ZVA(ZVA40):
	def __init__(self):
		'''
		A class to easily take and write data with the vna

		@Params
			vna object from skrf.vi (zva)

		'''
		ZVA40.__init__(self, address = 20)
		#you will want the ZVA to be connected when you initialize
	def write_data(self,name):

		self.get_network().write_touchstone(name)

class ESP(ESP300):
	def __init__(self):
		'''
		A class to control the ESP300 motor driver

		@Params
			visa instrument object
			current position
		'''
		#rm = visa.ResourceManager()
		#assumes only one resource
		#self.inst = rm.open_resource(rm.list_resources()[0])
		#print(self.inst.query("*IDN?"))

		ESP300.__init__(self, address = 1, current_axis = 1, always_wait_for_stop=True, delay = 0.1)

	def move(self, x):
		self.position = x
		self.wait_for_stop()
		time.sleep(1)

class LIA5209(object):
	def __init__(self):
		'''
		A class to interface with the EG&G Princetion Applied Research
		Lock-In Amplifier Model 5209
		'''
		self.inst = visa.ResourceManager().open_resource('GPIB0::6::INSTR')

	def get_output(self):
		self.inst.ask('OUT')

	def get_ID(self):
		self.inst.ask('ID')

	def D1(self, bool = 0, n = 0):
		if(bool):
			self.inst.ask('D1 n')
		else:
			self.inst.ask('D1 ' + str(n))

	def D2(self, bool = 0, n = 0):
		if(bool):
			self.inst.ask('D2 n')
		else:
			self.inst.ask('D2 ' + str(n))
