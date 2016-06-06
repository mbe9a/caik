'''
Alex Arsenovic, Michael Eller, Noah Sauber
UVA THZ CAI
'''

import decoder
import os
import cPickle as pickle


class image_data(object):
	'''
	kind is a projector mask set object ex: projector.hadamard(2, 50)
	'''
	def __init__(self, kind, image_name):
		self.kind = kind
		self.image_name = image_name
		self.data = {'primary' : dict([(decoder.mask2hex(mask), []) for mask in kind.primary_masks]), 'inverse' : dict([(decoder.mask2hex(mask), []) for mask in kind.inverse_masks])}

	def add_primary_data(self, mask, data):
		self.data['primary'][mask] = data

	def add_inverse_data(self, mask, data):
		self.data['inverse'][mask] = data

class data_structure(object):
	'''
	contains image_data
	'''
	def __init__(self, kind):
		self.name = kind.name
		self.data = {'primary' : dict([(decoder.mask2hex(mask), {}) for mask in kind.primary_masks]), 'inverse' : dict([(decoder.mask2hex(mask), {}) for mask in kind.inverse_masks])}

	@property
	def images(self):
		return ['primary ' + image for image in self.data['primary'].values()[0].keys()] + ['inverse ' + image for image in self.data['inverse'].values()[0].keys()]

	def add_image(self, img_data):
		for name in self.images:
			if img_data.image_name == name:
				return False
		if self.name == img_data.kind.name:
			for mask in self.data['primary'].keys():
				self.data['primary'][mask] = (img_data.image_name, img_data.data['primary'][mask])
			for mask in self.data['inverse'].keys():
				self.data['inverse'][mask] = (img_data.image_name, img_data.data['inverse'][mask])
			return True
		return False

def save(d_s, name, base_dir = os.getcwd()):
	pickle.dump(d_s, open(base_dir + name + '.p', 'wb'))

def load(name, base_dir = os.getcwd()):
	return pickle.load(open(base_dir + name + '.p', 'rb'))


	