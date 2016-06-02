'''
Alex Arsenovic, Michael Eller, Noah Sauber
UVA THZ CAI
'''

#graphic user interface for caik

from Tkinter import *
import tkFileDialog
import cai
import projector as pro
import decoder as deco
import encoder as enc
import instruments as inst

import skrf as rf




class GUI(Tk):

	def __init__(self, *args, **kwargs):
		Tk.__init__(self, *args, **kwargs)

		container = Frame(self)
		container.pack(side = "top", fill = "both", expand = True)
		container.grid_rowconfigure(0, weight = 1)
		container.grid_columnconfigure(0, weight = 1)

		self.cai = None
		self.cal = None
		self.kind = None

		self.frames = {}
		for F in (Initial, Image):
			page_name = F.__name__
			frame = F(container, self)
			self.frames[page_name] = frame

			frame.grid(row = 0, column = 0, sticky = "nsew")

		#status bar
		self.status = Label(self, text = "Hang by the bar. Put out the vibe.", bd = 1, relief = SUNKEN, anchor = W)
		self.status.pack(side = BOTTOM, fill = X)

		#menu
		self.menubar = Menu(self)

		self.filemenu = Menu(self.menubar, tearoff = 0)
		self.filemenu.add_command(label = "Open Cal...", command = self.open_cal)
		self.filemenu.add_command(label = "Save Cal...", command = self.save_cal)
		self.filemenu.add_separator()
		self.menubar.add_cascade(label = "File", menu = self.filemenu)

		self.config(menu=self.menubar)
		self.show_frame("Initial")

	def open_cal(self):
		f = tkFileDialog.askopenfilename(filetypes = [('Calibration', '.cal')])
		if f is None:
			print("Calibration load failed")
			return
		self.cal = rf.read(f)
		self.status.config(text = "Calibration loaded successfully")

	def save_cal(self):
		f = tkFileDialog.asksaveasfile(mode = 'w', defaultextension = ".cal")
		if f is None:
			self.status.config(text = "Calibration save failed")
			return
		self.cal.write(f)
		self.status.config(text = "Calibration saved successfully")

	def show_frame(self, page_name):
		frame = self.frames[page_name]
		frame.tkraise()

class Initial(Frame):
	def __init__(self, parent, controller):

		Frame.__init__(self, parent)

		self.start = IntVar()
		self.controller = controller
		self.cal_load = IntVar()


		Checkbutton(self, text = "Connect GPIB instruments", variable = self.start).grid(row = 0, column = 1, sticky = W)
		Checkbutton(self, text = "Load/Match", variable = self.cal_load).grid(row = 2, column = 1, sticky = W)

		Button(self, text = "Initialize", command = self.initialize).grid(row = 0)
		Button(self, text = "Next", command = self.to_image).grid(row = 6)
		Button(self, text = "Take Calibration", command = self.calibrate).grid(row = 2)

	def initialize(self):
		self.controller.cai = cai.CAI(start = self.start.get())

	def calibrate(self):
		if self.controller.cai is None:
			self.controller.status.config(text =  "CAI not intialized")
			return
		self.controller.status.config(text =  "Calibrating...")
		self.controller.cal = self.controller.cai.take_simple_cal(self.cal_load.get())
		self.controller.status.config(text =  "Calibration complete.")

	def to_image(self):
		if self.controller.cal is None:
			self.controller.status.config(text =  "No calibration selected")
		self.controller.show_frame("Image")


class Image(Frame):
	def __init__(self, parent, controller):

		Frame.__init__(self, parent)
		self.controller = controller

		#control variables
		self.method = StringVar()
		self.base_dir = StringVar()
		
		self.rank = IntVar()
		self.var = IntVar()
	
		#buttons
		Button(self, text = "Take Image", command = self.image).pack()
		Button(self, text = "Recalibrate", command = self.recalibrate).pack()

		Radiobutton(self, text = "Primary", variable = self.var, value = 0).pack()
		Radiobutton(self, text = "Inverted", variable = self.var, value = 1).pack()
		Radiobutton(self, text = "Both", variable = self.var, value = 2).pack()

		#options
		OptionMenu(self, self.method, "Hadamard", "Raster", "Bar").pack()

		#entries
		Entry(self, textvariable = self.rank).pack()
		Entry(self, textvariable = self.base_dir).pack()

		#labels
		Label(self, text = "Select resolution ").pack()
		Label(self, text = "Select an imaging method ").pack()


	def image(self):
		print 1

	def recalibrate(self):

		self.controller.show_frame("Initial")


root = GUI()
root.title("Terahertz Coded Aperture Imaging")

root.mainloop()