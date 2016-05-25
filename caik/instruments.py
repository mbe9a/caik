'''
Alex Arsenovic, Michael Eller, Noah Sauber
UVA THZ CAI
'''

import visa
from skrf.vi.vna import ZVA40
from skrf.vi.stages import ESP300
import numpy
import time

class ZVA(ZVA40):
	def __init__(self):
		'''
		A class to easily take and write data with the vna

		@Params
			vna object from skrf.vi (zva)

		'''
		ZVA40.__init__(self, address = 20)
		#you will want the ZVA to be connected when you initialize
		print "NOTE: ZVA40 has been connected."
	def write_data(self,name, format = 'ma'):

		self.get_network().write_touchstone(name, form = format)

class ESP(object):
	def __init__(self):
		'''
		A class to control the ESP300 motor driver

		@Params
			visa instrument object
			current position
		'''
		rm = visa.ResourceManager()
		self.inst = rm.open_resource('GPIB0::1::INSTR')
		#del self.inst.timeout
		self.current_axis = 1
		#ESP300.__init__(self, address = 1, current_axis = 1, always_wait_for_stop=True, delay = 0.1)
		print "NOTE: ESP Motor Driver has been connected."

	@property
	def position(self):
	    return float(self.inst.ask(str(self.current_axis)+"TP?")[0:4])

	@position.setter
	def position(self, x):
		self.inst.write(str(self.current_axis)+"PA"+str(x))


class LIA5209(object):
	def __init__(self):
		'''
		A class to interface with the EG&G Princeton Applied Research
		Lock-In Amplifier Model 5209
		'''
		self.inst = visa.ResourceManager().open_resource('GPIB0::6::INSTR')
		print "NOTE: LIA5209 has been connected."

	def get_output(self):
		return self.inst.ask('OUT')

	def get_ID(self):
		return self.inst.ask('ID')

	def D1(self, bool = 0, n = 0):
		if(bool):
			return self.inst.ask('D1 n')
		else:
			return self.inst.ask('D1 ' + str(n))

	def D2(self, bool = 0, n = 0):
		if(bool):
			return self.inst.ask('D2 n')
		else:
			return self.inst.ask('D2 ' + str(n))

class LIASR530(object):
	def __init__(self):
		self.inst = visa.ResourceManager().open_resource('GPIB0::23::INSTR')
		print "NOTE: SR530 has been connected."

	def get_output(self):
		return self.inst.ask('Q1')

class KEITHLEY(object):
	def __init__(self):
		'''
		Class to interface with the Keithley 2000 Multimeter
		'''
		self.inst = visa.ResourceManager().open_resource('GPIB0::8::INSTR')
		print "NOTE: Keithley Multimeter has been connected."

	def get_output(self):
		return self.inst.ask('READ?')