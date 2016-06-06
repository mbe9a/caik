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
		self.status = Label(self, text = 'Hang by the bar. Put out the vibe.', bd = 1, relief = SUNKEN, anchor = W)
		self.status.pack(side = BOTTOM, fill = X)

		#sidebar
		self.sidebar = Frame(self, bg = 'red')
		Button(self.sidebar, text = 'Home', command = lambda: self.show_frame('Home')).pack(fill = 'both', padx = 2, pady = 2)
		Button(self.sidebar, text = 'Control', command = lambda: self.show_frame('Control')).pack(fill = 'both', padx = 2, pady = 2)
		Button(self.sidebar, text = 'Calibrate', command = lambda: self.show_frame('Cal')).pack(fill = 'both', padx = 2, pady = 2)
		Button(self.sidebar, text = 'Capture', command = lambda: self.show_frame('Cap')).pack(fill = 'both', padx = 2, pady = 2)
		Button(self.sidebar, text = 'View', command = lambda: self.show_frame('View')).pack(fill = 'both', padx = 2, pady = 2)
		Button(self.sidebar, text = 'Exit').pack(side = BOTTOM, fill = 'both', padx = 2, pady = 2)
		Button(self.sidebar, text = 'Save').pack(side = BOTTOM, fill = 'both', padx = 2, pady = 2)

		self.sidebar.pack(side = LEFT, fill = Y)

		#container
		container.pack(side = 'top', fill = 'both', expand = True)
		container.grid_rowconfigure(0, weight = 1)
		container.grid_columnconfigure(0, weight = 1)

		#menu
		self.menubar = Menu(self)
		self.filemenu = Menu(self.menubar, tearoff = 0)
		self.filemenu.add_command(label = 'Open Cal...', command = self.open_cal)
		self.filemenu.add_command(label = 'Save Cal...', command = self.save_cal)
		self.filemenu.add_separator()
		self.menubar.add_cascade(label = 'File', menu = self.filemenu)
	
		self.config(menu=self.menubar)

		self.show_frame('Home')

		
	def open_cal(self):
		f = tkFileDialog.askopenfilename(filetypes = [('Calibration', '.cal')])
		if f is None:
			print('Calibration load failed')
			return
		self.cal = rf.read(f)
		self.status.config(text = 'Calibration loaded successfully')

	def save_cal(self):
		f = tkFileDialog.asksaveasfile(mode = 'w', defaultextension = '.cal')
		if f is None:
			self.status.config(text = 'Calibration save failed')
			return
		self.cal.write(f)
		self.status.config(text = 'Calibration saved successfully')

	def show_frame(self, page_name):
		frame = self.frames[page_name]
		frame.tkraise()


class Home(Frame):
	def __init__(self, parent, controller):

		Frame.__init__(self, parent)
		self.controller = controller

		Label(self, text = 'Welcome').pack()

class Control(Frame):
	def __init__(self, parent, controller):

		Frame.__init__(self, parent)
		self.controller = controller
				
		self.mirror_pos_c = DoubleVar()
		self.si_pos_c = DoubleVar()
		
		self.fpnts_c = IntVar()
		self.fstart_c = DoubleVar()
		self.fend_c = DoubleVar()
		
		self.connect = Button(self, text = 'Connect GPIB instruments', command = self.initialize)
		self.connect.pack(side = TOP, padx = 2, pady = 2)

	def initialize(self):
		self.controller.cai.start_esp()
		self.controller.cai.start_zva()

		self.fpnts_c.set(self.controller.cai.zva.get_f_npoints())
		self.fstart_c.set(self.controller.cai.zva.get_f_start()/1000000000)
		self.fend_c.set(self.controller.cai.zva.get_f_stop()/1000000000)

		self.connect.pack_forget()
		
		#esp
		self.mirror_pos = Entry(self, textvariable = self.mirror_pos_c)
		self.mirror_pos.grid(row = 3, column = 1)
		self.mirror_pos.bind('<Return>', self.move_mirror)
		Label(self, text = 'Mirror Position (mm)').grid(row = 3, column = 0, sticky = E)

		# self.si_pos = Entry(self, textvariable = self.si_pos_c)
		# self.si_pos.grid(row = 5, column = 1)
		# self.si_pos.bind('<Return>', self.move_si)
		# Label(self, text = 'Silicon Position (mm)').grid(row = 5, column = 0, sticky = E)

		#zva
		self.fpnts = Entry(self, textvariable = self.fpnts_c)
		self.fpnts.grid(row = 7, column = 1)
		self.fpnts.bind('<Return>', self.set_points)
		Label(self, text = 'Number of Data Points').grid(row = 7, column = 0, sticky = E)

		self.fstart = Entry(self, textvariable = self.fstart_c)
		self.fstart.grid(row = 9, column = 1)
		self.fstart.bind('<Return>', self.set_start)
		Label(self, text = 'Start Frequency (GHz)').grid(row = 9, column = 0, sticky = E)

		self.fend = Entry(self, textvariable = self.fend_c)
		self.fend.grid(row = 11, column = 1)
		self.fend.bind('<Return>', self.set_end)
		Label(self, text = 'End Frequency (GHz)').grid(row = 11, column = 0, sticky = E)

	def move_mirror(self, x):
		self.controller.cai.esp.current_axis = 1
		self.controller.cai.esp.position = self.mirror_pos_c.get()

	def move_si(self, x):
		self.controller.cai.esp.current_axis = 2
		self.controller.cai.esp.position = self.si_pos_c.get()

	def set_points(self, x):
		f = self.fpnts_c.get()
		if f < 2:
			f = 2
		if f > 400:
			f = 400
		self.controller.cai.zva.set_f_npoints(f)

	def set_start(self, x):
		f = self.fstart_c.get()
		if f < 500:
			f = 500
		if f >= self.fend_c.get():
			f = self.fend_c.get() - 1
		f = f*1000000000
		self.controller.cai.zva.set_f_start(f)

	def set_end(self, x):
		f = self.fend_c.get()
		if f > 750:
			f = 750
		if f <= self.fstart_c.get():
			f = self.fstart_c.get() - 1
		f = f*1000000000
		self.controller.cai.zva.set_f_stop(f)

class Cal(Frame):
	def __init__(self, parent, controller):

		Frame.__init__(self, parent)
		self.controller = controller

		self.cal_load = IntVar()

		Button(self, text = 'Take Calibration', command = self.calibrate).pack(side = TOP, padx = 5, pady = 5)
		Checkbutton(self, text = 'Load/Match', variable = self.cal_load).pack(side = TOP)

	def calibrate(self):
		if self.controller.cai is None:
			self.controller.status.config(text =  'CAI not intialized')
			return

		if hasattr(self.controller.cai, 'esp'):
			self.controller.status.config(text =  'Calibrating...')
			self.controller.cal = self.controller.cai.take_simple_cal(self.cal_load.get())
			self.controller.status.config(text =  'Calibration complete.')
			return
		
		self.controller.status.config(text =  'Calibration failed. One or more instruments not initialized.')
		

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
		Button(self, text = 'Take Image', command = self.image).pack()

		Radiobutton(self, text = 'Primary', variable = self.var_c, value = 0).pack()
		Radiobutton(self, text = 'Inverted', variable = self.var_c, value = 1).pack()
		Radiobutton(self, text = 'Both', variable = self.var_c, value = 2).pack()

		#options
		self.om = OptionMenu(self, self.method_c, 'hadamard', 'raster', 'bar')
		self.method_c.trace('w', self.update)
		self.om.pack()

		#entries
		self.scale = Entry(self, textvariable = self.scale_c)
		self.rank = Entry(self, textvariable = self.rank_c)
		self.xlen = Entry(self, textvariable = self.xlen_c)
		self.ylen = Entry(self, textvariable = self.ylen_c)

		#labels
		self.l_rank = Label(self, text = 'Select rank ')
		self.l_method = Label(self, text = 'Select an imaging method ')

	def update(self, n, m, x):
		f = self.method_c.get()

		if f == 'hadamard':
			self.rank.pack()
			self.scale.pack()
			self.xpos.pack_forget()
			self.ypos.pack_forget()

		if f == 'raster':
			self.rank.pack_forget()
			self.scale.pack()
			self.xlen.pack()
			self.ylen.pack()
		
		if f == 'bar':
			self.rank.pack()
			self.scale.pack()
			self.xlen.pack_forget()
			self.ylen.pack_forget()

	def image(self):
		f = self.var.get()
		if f is 'hadamard':
			obj = pro.F()
		self.controller.cai.take_hadamard_image(obj)

class View(Frame):
	def __init__(self, parent, controller):

		Frame.__init__(self, parent)
		self.controller = controller


root = GUI()
root.title('Terahertz Coded Aperture Imaging')
root.geometry('500x400')
root.resizable(0,0)
root.mainloop()