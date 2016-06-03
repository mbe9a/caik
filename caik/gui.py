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

		self.cai = cai.CAI()
		self.cal = None
		self.kind = None

		container = Frame(self)

		self.frames = {}
		for F in (Home, Control, Cal, Cap, View):
			page_name = F.__name__
			frame = F(container, self)
			self.frames[page_name] = frame
			frame.grid(row=0, column=0, sticky='nsew')

		#status bar
		self.status = Label(self, text = "Hang by the bar. Put out the vibe.", bd = 1, relief = SUNKEN, anchor = W)
		self.status.pack(side = BOTTOM, fill = X)

		# #sidebar
		self.sidebar = Frame(self, bg = "red")
		Button(self.sidebar, text = "Home", command = lambda: self.show_frame("Home")).pack(fill = "both", padx = 2, pady = 2)
		Button(self.sidebar, text = "Control", command = lambda: self.show_frame("Control")).pack(fill = "both", padx = 2, pady = 2)
		Button(self.sidebar, text = "Calibrate", command = lambda: self.show_frame("Cal")).pack(fill = "both", padx = 2, pady = 2)
		Button(self.sidebar, text = "Capture", command = lambda: self.show_frame("Cap")).pack(fill = "both", padx = 2, pady = 2)
		Button(self.sidebar, text = "View", command = lambda: self.show_frame("View")).pack(fill = "both", padx = 2, pady = 2)
		self.sidebar.pack(side = LEFT, fill = Y)

		#window
		container.pack(side = "top", fill = "both", expand = True)
		container.grid_rowconfigure(0, weight = 1)
		container.grid_columnconfigure(0, weight = 1)

		#menu
		self.menubar = Menu(self)
		self.filemenu = Menu(self.menubar, tearoff = 0)
		self.filemenu.add_command(label = "Open Cal...", command = self.open_cal)
		self.filemenu.add_command(label = "Save Cal...", command = self.save_cal)
		self.filemenu.add_separator()
		self.menubar.add_cascade(label = "File", menu = self.filemenu)
	
		self.config(menu=self.menubar)

		self.show_frame("Home")

		
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


class Home(Frame):
	def __init__(self, parent, controller):

		Frame.__init__(self, parent)
		self.controller = controller

		Label(self, text = "Welcome").pack()

class Control(Frame):
	def __init__(self, parent, controller):

		Frame.__init__(self, parent)
		self.controller = controller
		
		self.start = IntVar()
		
		self.mirror_pos = IntVar()
		self.mirror_pos.trace("w", self.move_mirror)
		
		self.si_pos = IntVar()
		self.si_pos.trace("w", self.move_si)

		self.fpnts = IntVar()
		self.fpnts.trace("w", self.set_points)
		self.fstart = IntVar()
		self.fstart.trace("w", self.set_start)
		self.fend = IntVar()
		self.fend.trace("w", self.set_end)
		
		self.connect = Button(self, text = "Connect GPIB instruments", command = self.initialize)
		self.connect.grid(row = 0, column = 1, sticky = W)

	def initialize(self):
		self.controller.cai.start_esp()
		self.controller.cai.start_zva()

		self.connect.grid_forget()
		#esp
		Entry(self, textvariable = self.mirror_pos).grid(row = 3, column = 1)
		Label(self, text = "Mirror Axis").grid(row = 3, column = 0, sticky = E)

		Entry(self, textvariable = self.si_pos).grid(row = 5, column = 1)
		Label(self, text = "Silicon Axis").grid(row = 5, column = 0, sticky = E)

		#zva
		Entry(self, textvariable = self.fpnts).grid(row = 7, column = 1)
		Label(self, text = "Number of Data Points").grid(row = 7, column = 0, sticky = E)

		Entry(self, textvariable = self.fstart).grid(row = 9, column = 1)
		Label(self, text = "Start Frequency").grid(row = 9, column = 0, sticky = E)

		Entry(self, textvariable = self.fend).grid(row = 11, column = 1)
		Label(self, text = "End Frequency").grid(row = 11, column = 0, sticky = E)

	def move_mirror(self, n, m, x):
		self.controller.esp.current_axis = 1
		self.controller.cai.esp.position = mirror_pos

	def move_si(self, n, m, x):
		self.controller.esp.current_axis = 2
		self.controller.cai.esp.position = si_pos

	def set_points(self, n, m, x):
		self.controller.cai.zva.f_npoints = self.fpnts

	def set_start(self, n, m, x):
		self.controller.cai.zva.f_start = self.fstart

	def set_end(self, n, m , x):
		self.controller.cai.zva.f_stop = self.fend

class Cal(Frame):
	def __init__(self, parent, controller):

		Frame.__init__(self, parent)
		self.controller = controller

		self.cal_load = IntVar()

		Checkbutton(self, text = "Load/Match", variable = self.cal_load).grid(row = 2, column = 1, sticky = W)
		Button(self, text = "Take Calibration", command = self.calibrate).grid(row = 2)

	def calibrate(self):
		if self.controller.cai is None:
			self.controller.status.config(text =  "CAI not intialized")
			return
		self.controller.status.config(text =  "Calibrating...")
		self.controller.cal = self.controller.cai.take_simple_cal(self.cal_load.get())
		self.controller.status.config(text =  "Calibration complete.")


class Cap(Frame):
	def __init__(self, parent, controller):

		Frame.__init__(self, parent)
		self.controller = controller

		#control variables
		self.method_c = StringVar()
		self.var_c = IntVar()
		self.scale_c = IntVar()
		self.xlen_c = IntVar()
		self.ylen_c = IntVar()
		self.rank_c = IntVar()


		#buttons
		Button(self, text = "Take Image", command = self.image).pack()

		Radiobutton(self, text = "Primary", variable = self.var_c, value = 0).pack()
		Radiobutton(self, text = "Inverted", variable = self.var_c, value = 1).pack()
		Radiobutton(self, text = "Both", variable = self.var_c, value = 2).pack()

		#options
		self.om = OptionMenu(self, self.method_c, "hadamard", "raster", "bar")
		self.method_c.trace("w", self.update)
		self.om.pack()

		#entries
		self.scale = Entry(self, textvariable = self.scale_c)
		self.rank = Entry(self, textvariable = self.rank_c)
		self.xlen = Entry(self, textvariable = self.xlen_c)
		self.ylen = Entry(self, textvariable = self.ylen_c)

		#labels
		self.l_rank = Label(self, text = "Select rank ")
		self.l_method = Label(self, text = "Select an imaging method ")

	def update(self, n, m, x):
		f = self.method_c.get()

		if f == "hadamard":
			self.rank.pack()
			self.scale.pack()
			self.xpos.pack_forget()
			self.ypos.pack_forget()

		if f == "raster":
			self.rank.pack_forget()
			self.scale.pack()
			self.xlen.pack()
			self.ylen.pack()
		
		if f == "bar":
			self.rank.pack()
			self.scale.pack()
			self.xlen.pack_forget()
			self.ylen.pack_forget()

	def image(self):
		f = self.var.get()
		if f is "hadamard":
			obj = pro.F()
		self.controller.cai.take_hadamard_image(obj)

class View(Frame):
	def __init__(self, parent, controller):

		Frame.__init__(self, parent)
		self.controller = controller


root = GUI()
root.title("Terahertz Coded Aperture Imaging")
root.geometry("500x400")
root.resizable(0,0)
root.mainloop()