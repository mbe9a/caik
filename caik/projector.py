'''
Alex Arsenovic, Michael Eller, Noah Sauber
UVA THZ CAI
'''

import win32com.client
from PIL import Image, ImageDraw
import encoder
import os
from enum import Enum
import MSO, MSPPT
import csv
from collections import namedtuple

g = globals()
for c in dir(MSO.constants):    g[c] = getattr(MSO.constants, c)
for c in dir(MSPPT.constants):  g[c] = getattr(MSPPT.constants, c)

#class to hold variables for a bar power point
class bar(object):
	def __init__(self, scale, base_dir = os.getcwd(), variant = 'primary'):
		self.base_dir = base_dir
		self.parts = parts
		self.variant = variant

	@property
	def path(self):
		return self.base_dir + '\\SlideShows\\bar\\bar_' + self.variant + '_' + str(self.parts) + '.pptx'
	
#class to hold variables for a raster power point
class raster(object):
	def __init__(self, x_parts, y_parts, scale,  base_dir = os.getcwd(), variant = 'primary'):
		self.base_dir = base_dir
		self.variant = variant
		self.x_parts = x_parts
		self.y_parts = y_parts
		self.scale = scale

	@property
	def path(self):
		return self.base_dir + '\\SlideShows\\raster\\raster_' + self.variant + '_' + str(self.x_parts) + '_' + str(self.y_parts) + '_' + str(self.scale) + '.pptx'
	
#class to hold variables for a hadamard power point
class hadamard(object):
	def __init__(self, rank, scale, base_dir = os.getcwd(), variant = 'primary'):
		self.base_dir = base_dir
		self.variant = variant
		self.rank = rank
		self.scale = scale

	@property
	def hadamard_encoder(self):
		return encoder.Hadamard(self.rank)
	
	@property
	def raw_masks(self):
		return self.hadamard_encoder.raw_masks
	
	@property
	def primary_masks(self):
		return self.hadamard_encoder.primary_masks
	
	@property
	def inverse_masks(self):
		return self.hadamard_encoder.inverse_masks
	
	@property
	def path(self):
		return self.base_dir + '\\Slide Shows\\hadamard\\hadamard_' + self.variant + '_' + str(self.rank) + '_' + str(self.scale) + '\\hadamard_' + self.variant + '_' + str(self.rank) + '_' + str(self.scale) + '.pptx'
	
#class to hold variables for a random resolution/pattern power point
class random(object):
	def __init__(self, resolution, scale, base_dir = os.getcwd(), variant = 'primary'):
		self.base_dir = base_dir
		self.variant = variant
		self.resolution = resolution
		self.scale = scale

	@property
	def path(self):
		return self.base_dir + '\\Slide Shows\\random\\random_' + self.variant + '_' + str(self.res) + '_' + str(self.scale) + '.pptx'
	
#class to hold variables for a walsh power point
class walsh(object):
	def __init__(self, rank, scale, base_dir = os.getcwd(), variant = 'primary'):
		self.base_dir = base_dir
		self.variant = variant
		self.rank = rank
		self.scale = scale

	@property
	def path(self):
		return self.base_dir + '\\Slide Shows\\walsh\\walsh_' + self.variant + '_' + str(self.rank) + '.pptx'
	

class PPT(object):
	
	'''
	this is a class intended to serve as the link between cai and our current projection system --> powerpoint.
	code assumes there is a folder called 'Slide Shows' (in working directory) that contains
	a folder for each type of presentation -- this can be modified and is not permanent.
	the folders are also created on initializing a ppt_generator object

	'''
	def __init__(self, kind):
		self.kind = kind

	#opens the given pptx and starts the slide show
	def start_pres(self):
		Application = win32com.client.Dispatch("Powerpoint.Application")
		Presentation = Application.Presentations.Open(FileName = self.kind.path)
		Presentation.SlideShowSettings.Run()
		self.SS = Application.SlideShowWindows(1)
		self.SS.View.First()

	#go to first slide
	def first_slide(self):
		self.SS.View.First()

	#show next slide
	def next_slide(self):
		self.SS.View.Next()

	#pick slide by number
	def show_slide(self, slide):
		self.SS.View.GotoSlide(slide)

	#go to previous slide
	def previous_slide(self):
		self.SS.View.Previous()

	#go to last slide
	def last_slide(self):
		self.SS.View.Last()

	#close the slide show
	def close_pres(self):
		self.SS.Exit()

#class to create powerpoints
class ppt_generator(object):
	def __init__(self, base_dir = os.getcwd()):
		self.base_dir = base_dir
		if not os.path.exists(self.base_dir + '\\Slide Shows'):
			os.mkdir('Slide Shows')
			os.chdir('Slide Shows')
			os.mkdir('bar')
			os.mkdir('raster')
			os.mkdir('hadamard')
			os.mkdir('random')
			os.mkdir('walsh')
			os.chdir('..')

	#create bar slide set
	def gen_bar_set(self, bar):
		Application = win32com.client.Dispatch("PowerPoint.Application")
		Presentation = Application.Presentations.Add()
		height = Presentation.PageSetup.SlideHeight
		width = Presentation.PageSetup.SlideWidth
		inc = width/bar.parts
		both = (bar.variant == 'both')
		inverse = (bar.variant == 'inverse')
		primary = (bar.variant == 'primary')
		#make the slides --> slides are created in reverse order, so the loop runs backwards
		if inverse or both:
			for x in range(bar.parts - 1, -1,-1):
				#make a slide
				slide = Presentation.Slides.Add(1, 12)
				#black background
				background = slide.ColorScheme.Colors(1).RGB = rgb(255,255,255)
				bar = slide.Shapes.AddShape(msoShapeRectangle,x*inc,0,inc,height)
				bar.Fill.ForeColor.RGB = 0
		if primary or both:
			for x in range(bar.parts - 1, -1,-1):
				#make a slide
				slide = Presentation.Slides.Add(1, 12)
				#black background
				background = slide.ColorScheme.Colors(1).RGB = 0
				bar = slide.Shapes.AddShape(msoShapeRectangle,x*inc,0,inc,height)
				bar.Fill.ForeColor.RGB = rgb(255,255,255)
		#make last (first) slide
		slide = Presentation.Slides.Add(1, 12)
		#black background
		background = slide.ColorScheme.Colors(1).RGB = 0
		Presentation.SaveAs(self.base_dir + '\\Slide Shows\\bar\\bar_' + bar.variant + '_' + str(bar.parts))
		os.system("taskkill /im powerpnt.exe /f")

	#create raster slide set
	def gen_raster_set(self, raster):
		scale = raster.scale/100.
		Application = win32com.client.Dispatch("PowerPoint.Application")
		Presentation = Application.Presentations.Add()
		height = Presentation.PageSetup.SlideHeight
		width = Presentation.PageSetup.SlideWidth
		x_inc = height/raster.x_parts*scale
		y_inc = height/raster.y_parts*scale
		both = (raster.variant == 'both')
		inverse = (raster.variant == 'inverse')
		primary = (raster.variant == 'primary')
		if inverse or both:
			for y in range (raster.y_parts - 1, -1, -1):
				for x in range (raster.x_parts - 1, -1, -1):
					slide = Presentation.Slides.Add(1,12)
					background = slide.ColorScheme.Colors(1).RGB = rgb(255, 255, 255)
					pixel = slide.Shapes.AddShape(msoShapeRectangle, (width - height*scale)/2 + x*x_inc, 
						(height - height*scale)/2 + y*y_inc, x_inc, y_inc)
					pixel.Fill.ForeColor.RGB = 0
		if primary or both:
			for y in range (raster.y_parts - 1, -1, -1):
				for x in range (raster.x_parts - 1, -1, -1):
					slide = Presentation.Slides.Add(1,12)
					background = slide.ColorScheme.Colors(1).RGB = 0
					pixel = slide.Shapes.AddShape(msoShapeRectangle, (width - height*scale)/2 + x*x_inc, 
						(height - height*scale)/2 + y*y_inc, x_inc, y_inc)
					pixel.Fill.ForeColor.RGB = rgb(255, 255, 255)
		slide = Presentation.Slides.Add(1, 12)
		background = slide.ColorScheme.Colors(1).rgb = 0
		Presentation.SaveAs(self.base_dir + '\\Slide Shows\\raster\\raster_' + raster.variant + '_' + str(raster.x_parts) + '_' + str(raster.y_parts) + '_' + str(raster.scale))
		os.system("taskkill /im powerpnt.exe /f")

	#create hadamard set
	def gen_hadamard_set(self, hadamard):
		scale = hadamard.scale/100.
		raw_masks = hadamard.raw_masks
		canvas_size = hadamard.hadamard_encoder.canvas_size

		matrixList = []
		for binary in hadamard.primary_masks:
			matrixList.append(decoder.bin2hex(binary))

		invML = []
		for binary in hadamard.inverse_masks:
			invML.append(decoder.bin2hex(binary))

		Application = win32com.client.Dispatch('PowerPoint.Application')
		Presentation = Application.Presentations.Add()
		height = Presentation.PageSetup.SlideHeight
		width = Presentation.PageSetup.SlideWidth

		both = (hadamard.variant == 'both')
		inverse = (hadamard.variant == 'inverse')
		primary = (hadamard.variant == 'primary')

		total = (2**hadamard.rank)**2 + 1
		if both:
			total = 2*(2**hadamard.rank)**2 + 1

		name = 'Slide Shows\\hadamard\\hadamard_' +  hadamard.variant + '_' + str(hadamard.rank) + '_' + str(hadamard.scale)
		if not os.path.exists(name):
			os.mkdir(name)

		with open(name + '\\map.csv', 'wb') as outfile:
			fieldnames = ['slide', 'mask in hex']
			writer = csv.DictWriter(outfile, fieldnames = fieldnames)
			writer.writeheader()
			count = 2

			if inverse or both:
				for x in range ((len(raw_masks)) - 1, -1, -1):
					#make a slide
					slide = Presentation.Slides.Add(1, 12)
					#black background
					background = slide.ColorScheme.Colors(1).RGB = 0
					#make base image
					image = Image.new('RGB', (canvas_size, canvas_size), (255, 255, 255))
					draw = ImageDraw.Draw(image)
					#draw image
					matrix = raw_masks[x]
					encoder.draw_hadamard_mask(matrix, canvas_size, 0, 0, 2, draw)
					#save image in pwd
					image.save("mask.png")

					#write to csv map file (for decode)
					writer.writerow({'slide': str(total - count + 2), 'mask in hex': invML[x]})

					#add mask image to slide
					mask = slide.Shapes.AddPicture(FileName = os.getcwd() + '\\mask.png', 
						LinkToFile = False, SaveWithDocument = True, Left = (width - height*scale)/2, Top = (height - height*scale)/2, 
						Width = height*scale, Height = height*scale)
					count += 1

			if primary or both:
				for x in range ((len(hm.matrixList)) - 1, -1, -1):
					slide = Presentation.Slides.Add(1, 12)
					background = slide.ColorScheme.Colors(1).RGB = 0
					image = Image.new('RGB', (canvas_size, canvas_size), (255, 255, 255))
					draw = ImageDraw.Draw(image)

					matrix = encoder.inverse(raw_masks[x])
					encoder.draw_hadamard_mask(matrix, canvas_size, 0, 0, 2, draw)
					image.save("mask.png")

					writer.writerow({'slide': str(total - count + 2), 'mask in hex': matrixList[x]})
					
					mask = slide.Shapes.AddPicture(FileName = os.getcwd() + '\\mask.png', 
						LinkToFile = False, SaveWithDocument = True, Left = (width - height*scale)/2, Top = (height - height*scale)/2, 
						Width = height*scale, Height = height*scale)
					count += 1

		#make last (first) slide
		slide = Presentation.Slides.Add(1, 12)
		#black background
		background = slide.ColorScheme.Colors(1).RGB = 0
		#save and exit
		Presentation.SaveAs(self.base_dir + '\\Slide Shows\\hadamard\\hadamard_' +  hadamard.variant + '_' + str(hadamard.rank) + '_' + str(hadamard.scale) + '\\hadamard_' + hadamard.variant + '_' + str(hadamard.rank) + '_' + str(hadamard.scale))
		os.system("taskkill /im powerpnt.exe /f")

	def gen_random_set(self, random):
		raise NotImplementedError

	def gen_walsh_set(self, walsh):
		raise NotImplementedError


#kill the ppt app
def kill_pptx():
	os.system('taskkill /im powerpnt.exe /f')

#calculate rgb values
def rgb(r,g,b):
    return r*256**2 + g*256 + b