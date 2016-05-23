'''
Alex Arsenovic, Michael Eller, Noah Sauber
UVA THZ CAI
'''

import numpy
import time
import win32com.client

class PPT(object):

	def __init__(self, name, kind = "hadamard", rank = 1):
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

	def run(self):
	    for x in range (0, self.Presentation.Slides.Count - 1):
	        time.sleep(2)
	        self.SS.View.Next()
	    os.system("taskkill /im powerpnt.exe /f")


	def show_slide(self, num):
		SlideShowWindows(1).View.GotoSlide(num)

	def restart(self):
		self.Application = win32com.client.Dispatch("PowerPoint.Application")
