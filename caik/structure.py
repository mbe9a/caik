'''
Alex Arsenovic, Michael Eller, Noah Sauber
UVA THZ CAI
'''

import decoder
import os
import cPickle as pickle

class cal_set(object):
	'''
	contains cals for each hadamard mask of a given rank
	'''
	def __init__(self, kind):
		self.kind = kind
		self.data = {'primary' : {decoder.mask2hex(mask) : None for mask in kind.primary_masks}, 'inverse' : {decoder.mask2hex(mask) : None for mask in kind.inverse_masks}}

	def write_pickle(self, base_dir = os.getcwd()):
		pickle.dump(self, open(base_dir + '/' + self.kind.name + '_cal_set.p', 'wb'))

class image_data(object):
	'''
	kind is a projector mask set object ex: projector.hadamard(2, 50)
	'''
	def __init__(self, kind, image_name):
		self.kind = kind
		self.image_name = image_name
		self.data = {'primary' : {decoder.mask2hex(mask) : [] for mask in kind.primary_masks}, 'inverse' : {decoder.mask2hex(mask) : [] for mask in kind.inverse_masks}}

	def add_primary_data(self, mask, data):
		self.data['primary'][mask] = data

	def add_inverse_data(self, mask, data):
		self.data['inverse'][mask] = data

	def write_pickle(self, base_dir = os.getcwd()):
		pickle.dump(self, open(base_dir + '/' + self.image_name + '.p', 'wb'))

class data_structure(object):
	'''
	contains image_data
	'''
	def __init__(self, kind):
		self.kind = kind
		self.name = kind.name
		self.data = {'primary' : {decoder.mask2hex(mask) : {} for mask in kind.primary_masks}, 'inverse' : {decoder.mask2hex(mask) : {} for mask in kind.inverse_masks}}

	@property
	def images(self):
		return [image for image in self.data['primary'].values()[0].keys()] + [image for image in self.data['inverse'].values()[0].keys()]

	def add_image(self, img_data):
		for name in self.images:
			if img_data.image_name == name:
				return False
		if self.name == img_data.kind.name:
			for mask in self.data['primary'].keys():
				self.data['primary'][mask][img_data.image_name] = img_data.data['primary'][mask]
			for mask in self.data['inverse'].keys():
				self.data['inverse'][mask][img_data.image_name] = img_data.data['inverse'][mask]
			return True
		return False

	def get_image(self, image_name):
		if image_name not in self.images:
			raise AttributeError('bad image name')
			return False

		image = image_data(self.kind, image_name)
		for mask in self.data['primary'].keys():
			image.data['primary'][mask] = self.data['primary'][mask][image_name]

		for mask in self.data['inverse'].keys():
			image.data['inverse'][mask] = self.data['inverse'][mask][image_name]

		return image

	def write_pickle(self, name, base_dir = os.getcwd()):
		pickle.dump(self, open(base_dir + '/' + name + '.p', 'wb'))

def read(name, base_dir = os.getcwd()):
	return pickle.load(open(base_dir + '/' + name + '.p', 'rb'))


	