'''
Alex Arsenovic, Michael Eller, Noah Sauber
UVA THZ CAI
'''

import win32com.client

class PPT(object):

	def __init__(self, kind = 'hadamard', rank = 1):
		accepted_kinds = {'hadamard', 'bar', 'raster'}

		if kind in accepted_kinds:
			self.name = name
			self.kind = kind
			self.rank = rank
			self.Application = win32com.client.Dispatch("PowerPoint.Application")
			self.Presentation = self.Application.Presentations.Open(FileName = str(self.name))
			self.SS = self.Application.SlideShowWindows(1)
			print "NOTE: Projector has been initialized."

		else:
			raise ValueError('bad kind')

	def show_slide(self, num):
		SlideShowWindows(1).View.GotoSlide(num)

	def restart(self):
		self.Application = win32com.client.Dispatch("PowerPoint.Application")
