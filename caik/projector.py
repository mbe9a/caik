'''
Alex Arsenovic, Michael Eller, Noah Sauber
UVA THZ CAI
'''

import win32com.client
from PIL import Image, ImageDraw
import cai
import os
from enum import Enum
import MSO, MSPPT
import csv

g = globals()
for c in dir(MSO.constants):    g[c] = getattr(MSO.constants, c)
for c in dir(MSPPT.constants):  g[c] = getattr(MSPPT.constants, c)

class PPT(object):
	
	'''
	this is a class intended to serve as the link between cai and our current projection system --> powerpoint
	code assumes there is a folder called 'Slide Shows' (in working directory) that contains
	a folder for each type of presentation -- this can be modified and is not permanent

	'''
	def __init__(self):
		#both enums are used to pick the correct pptx easily
		#redundant for now
		self.accepted_kinds = Enum('kind', 'hadamard random raster bar walsh')
		self.slide_show_variants = Enum('variants', 'primary inverse both')
		self.base_dir = os.getcwd()

	#opens the given pptx and starts the slide show
	def start_pres(self, kind = 'hadamard', variant = 'primary', random_res = 8, rank = 3, scale = 50, start = 0, bar_parts = 25, raster_xparts = 8, raster_yparts = 8):
		self.check_kind(kind)
		self.check_variant(variant)
		self.check_scale(scale)

		#formulate path to presentation
		if kind == 'bar':
			name = base_dir + '\\SlideShows\\bar\\bar_' + variant + '_' + str(bar_parts) + '.pptx'
		
		elif kind == 'raster':
			name = base_dir + '\\SlideShows\\raster\\raster_' + variant + '_' + str(raster_xparts) + '_' + str(raster_yparts) + '_' + str(scale) + '.pptx'
		
		elif kind == 'hadamard':
			name = base_dir + '\\Slide Shows\\hadamard\\hadamard_' + variant + '_' + str(rank) + '_' + str(scale) + '.pptx'

		elif kind == 'random':
			name = base_dir + '\\Slide Shows\\random\\random_' + variant + '_' + str(random_res) + '_' + str(scale) + '.pptx'

		else:
			name = base_dir + '\\Slide Shows\\walsh\\walsh_' + variant + '_' + str(rank) + '.pptx'

		#start presentation
		Application = win32com.client.Dispatch("Powerpoint.Application")
		Presentation = Application.Presentations.Open(FileName = name)
		Presentation.SlideShowSettings.Run()
		self.SS = Application.SlideShowWindows(1)
		self.SS.View.First()

	#check kind
	def check_kind(self, kind):
		for member in self.accepted_kinds:
			if variant == member.name:
				break
			else:
				raise ValueError('bad slide show variant')
		return True

	#check variant
	def check_variant(self, variant):
		for member in self.slide_show_variants:
			if variant == member.name:
				break
			else:
				raise ValueError('bad slide show variant')
		return True

	#check scale
	def check_scale(self, scale):
		if scale < 1 or scale > 100:
			raise ValueError('bad scale')

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

#create bar slide set
def gen_bar_set(parts, primary = True, inverse = False):
	Application = win32com.client.Dispatch("PowerPoint.Application")
	Presentation = Application.Presentations.Add()
	height = Presentation.PageSetup.SlideHeight
	width = Presentation.PageSetup.SlideWidth
	inc = width/parts
	both = primary and inverse
	#make the slides --> slides are created in reverse order, so the loop runs backwards
	if inverse or both:
		for x in range(parts - 1, -1,-1):
			#make a slide
			slide = Presentation.Slides.Add(1, 12)
			#black background
			background = slide.ColorScheme.Colors(1).RGB = rgb(255,255,255)
			bar = slide.Shapes.AddShape(msoShapeRectangle,x*inc,0,inc,height)
			bar.Fill.ForeColor.RGB = 0
	if primary or both:
		for x in range(parts - 1, -1,-1):
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
	variant = 'primary'
	if both:
		variant = 'both'
	elif inverse:
		variant = 'inverse'
	Presentation.SaveAs('C:\\Users\\Michael\\Dropbox\\VECAP\\CAI\\Imaging\\Slide Shows\\bar\\bar_' + variant + '_' + str(parts))
	os.system("taskkill /im powerpnt.exe /f")

#create raster slide set
def gen_raster_set(x_parts, y_parts, scale, primary = True, inverse = False):
	scale /= 100.
	Application = win32com.client.Dispatch("PowerPoint.Application")
	Presentation = Application.Presentations.Add()
	height = Presentation.PageSetup.SlideHeight
	width = Presentation.PageSetup.SlideWidth
	x_inc = height/x_parts*scale
	y_inc = height/y_parts*scale
	both = primary and inverse
	if inverse or both:
		for y in range (y_parts - 1, -1, -1):
			for x in range (x_parts - 1, -1, -1):
				slide = Presentation.Slides.Add(1,12)
				background = slide.ColorScheme.Colors(1).RGB = rgb(255, 255, 255)
				pixel = slide.Shapes.AddShape(msoShapeRectangle, (width - height*scale)/2 + x*x_inc, 
					(height - height*scale)/2 + y*y_inc, x_inc, y_inc)
				pixel.Fill.ForeColor.RGB = 0
	if primary or both:
		for y in range (y_parts - 1, -1, -1):
			for x in range (x_parts - 1, -1, -1):
				slide = Presentation.Slides.Add(1,12)
				background = slide.ColorScheme.Colors(1).RGB = 0
				pixel = slide.Shapes.AddShape(msoShapeRectangle, (width - height*scale)/2 + x*x_inc, 
					(height - height*scale)/2 + y*y_inc, x_inc, y_inc)
				pixel.Fill.ForeColor.RGB = rgb(255, 255, 255)
	slide = Presentation.Slides.Add(1, 12)
	background = slide.ColorScheme.Colors(1).rgb = 0
	scale = inst(scale*100)
	variant = 'primary'
	if both:
		variant = 'both'
	elif inverse:
		variant = 'inverse'
	Presentation.SaveAs('C:\\Users\\Michael\\Dropbox\\VECAP\\CAI\\Imaging\\Slide Shows\\raster\\raster_' + variant + '_' + str(x_parts) + '_' + str(y_parts) + '_' + str(scale))
	os.system("taskkill /im powerpnt.exe /f")

#create hadamard set
def gen_hadamard_set(rank, scale, primary = True, inverse = False):
	scale /= 100.
	hm = cai.CAI(dimension = rank)

	matrixList = []
	for binary in cai.list2bn(rank, hm.matrixList):
		matrixList.append("{0:#0{1}x}".format(int('0b'+''.join(binary), base = 0), (2**rank)**2/4 + 2))

	invML = []
	for binary in cai.list2bn(rank, cai.inverse_ML(hm.matrixList)):
		invML.append("{0:#0{1}x}".format(int('0b'+''.join(binary), base = 0), (2**rank)**2/4 + 2))

	Application = win32com.client.Dispatch('PowerPoint.Application')
	Presentation = Application.Presentations.Add()
	height = Presentation.PageSetup.SlideHeight
	width = Presentation.PageSetup.SlideWidth

	both = primary and inverse

	total = (2**rank)**2 + 1
	if both:
		total = 2*(2**rank)**2 + 1

	variant = 'primary'
	if both:
		variant = 'both'
	elif inverse:
		variant = 'inverse'

	name = 'C:\\Users\\Michael\\Dropbox\\VECAP\\CAI\\Imaging\\Slide Shows\\hadamard\\hadamard_' +  variant + '_' + str(rank) + '_' + str(int(scale*100))
	os.mkdir(name)
	with open(name + '\\map.csv', 'wb') as outfile:
		fieldnames = ['slide', 'mask in hex']
		writer = csv.DictWriter(outfile, fieldnames = fieldnames)
		writer.writeheader()
		count = 2

		if inverse or both:

			for x in range ((len(hm.matrixList)) - 1, -1, -1):
				#make a slide
				slide = Presentation.Slides.Add(1, 12)
				#black background
				background = slide.ColorScheme.Colors(1).RGB = 0
				#make base image
				image = Image.new('RGB', (hm.canvasSize, hm.canvasSize), (255, 255, 255))
				draw = ImageDraw.Draw(image)
				#draw image
				matrix = hm.matrixList[x]
				cai.drawH(matrix, hm.canvasSize, 0, 0, 2, draw)
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
				image = Image.new('RGB', (hm.canvasSize, hm.canvasSize), (255, 255, 255))
				draw = ImageDraw.Draw(image)

				matrix = cai.inverse(hm.matrixList[x])
				cai.drawH(matrix, hm.canvasSize, 0, 0, 2, draw)
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
	scale = int(scale*100)
	Presentation.SaveAs('C:\\Users\\Michael\\Dropbox\\VECAP\\CAI\\Imaging\\Slide Shows\\hadamard\\hadamard_' +  variant + '_' + str(rank) + '_' + str(scale) + '\\hadamard_' + variant + '_' + str(rank) + '_' + str(scale))
	os.system("taskkill /im powerpnt.exe /f")

#kill the ppt app
def kill_pptx(void):
	os.system('taskkill /im powerpnt.exe /f')

#calculate rgb values
def rgb(r,g,b):
    return r*256**2 + g*256 + b