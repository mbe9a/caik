'''
Alex Arsenovic, Michael Eller, Noah Sauber
UVA THZ CAI
'''

#graphic user interface for caik

#base python imports
from Tkinter import *
import ttk
import tkFileDialog
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
#caik imports
import cai
import projector as pro
import decoder as deco
import encoder as enc
import instruments as inst
#additional imports
import skrf as rf




class GUI(Tk):
	def __init__(self, *args, **kwargs):
		Tk.__init__(self, *args, **kwargs)

		self.cai = cai.CAI()
		self.cal = None
		self.kind = None
		self.name = None

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
		self.filemenu.add_command(label = 'New File')
		self.filemenu.add_command(label = 'Open File')
		self.filemenu.add_command(label = 'Save')
		self.filemenu.add_command(label = 'Save as...')
		self.filemenu.add_separator()
		self.filemenu.add_command(label = 'Open Cal...', command = self.open_cal)
		self.bind_all('<Control-Alt-o>', self.open_cal)
		self.filemenu.add_command(label = 'Save Cal...', command = self.save_cal)
		self.bind_all('<Control-Alt-s>', self.save_cal)
		self.filemenu.add_separator()
		self.menubar.add_cascade(label = 'File', menu = self.filemenu)
	
		self.config(menu=self.menubar)

		self.show_frame('Cal')

		
	def open_cal(self, event = '<Control-Alt-o>'):
		f = tkFileDialog.askopenfilename(filetypes = [('Calibration', '.cal')])
		if f is None:
			print('Calibration load failed')
			return
		self.cal = rf.read(f)
		self.status.config(text = 'Calibration loaded successfully')
		self.show_frame('Cal')

	def save_cal(self, event = '<Control-Alt-s>'):
		f = tkFileDialog.asksaveasfile(mode = 'w', defaultextension = '.cal')
		if f is None:
			self.status.config(text = 'Calibration save failed')
			return
		self.cal.write(f)
		self.status.config(text = 'Calibration saved successfully')

	def show_frame(self, page_name):
		frame = self.frames[page_name]
		if page_name is 'Cal':
			if self.cal != None:
				frame.show_cal()
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

		self.match_load = IntVar()
		
		self.top_frame = Frame(self, bg = 'green')
		Button(self.top_frame, text = 'Take Calibration', command = self.show_cal).pack(side = LEFT, padx = 5, pady = 5)
		Checkbutton(self.top_frame, text = 'Load/Match', variable = self.match_load).pack(side = LEFT)
		self.top_frame.pack(side = TOP, fill = X)

		self.smith = Frame(self, bg = 'blue')
		self.smith.pack(side = TOP, fill = BOTH, expand = True)
		self.cal_smith = Label(self.smith)


		if hasattr(self.controller.cal, 'plot_caled_ntwks'):
			self.show_cal()

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

	def show_cal(self, attr='s_smith', show_legend=False,**kwargs):
		self.controller.cal.plot_caled_ntwks()
		plt.savefig('cal_smith.jpg')
		image = Image.open("cal_smith.jpg")
		photo = ImageTk.PhotoImage(image)

		self.cal_smith.pack_forget()
		self.cal_smith = Label(self.smith,image = photo)
		self.cal_smith.image = photo
		self.cal_smith.pack(side = TOP, fill = BOTH, expand = True)
		plt.clf()

class Cap(Frame):
	def __init__(self, parent, controller):

		Frame.__init__(self, parent)
		self.controller = controller
		self.params = Frame(self, bg = 'blue')

		#hadamard interface
		self.scale_c = IntVar()
		self.scale_l = Label(self.params, text = "Scale")
		self.scale = Entry(self.params, textvariable = self.scale_c)

		self.rank_c = IntVar()
		self.rank_l = Label(self.params, text = 'Rank')
		self.rank = Entry(self.params, textvariable = self.rank_c)

		self.take_c = BooleanVar()
		self.take_c.set(True)
		self.take = Checkbutton(self.params, text = 'Take', variable = self.take_c)

 		self.mask_delay_c = IntVar()
 		self.mask_delay_c.set(1)
		self.mask_delay_l = Label(self.params, text = 'Delay between masks')
		self.mask_delay = Entry(self.params, textvariable = self.mask_delay_c)

 		self.duty_c = DoubleVar()#Not implemented
 		
 		self.num_meas_c = IntVar()
 		self.num_meas_c.set(1)
 		self.num_meas_l = Label(self.params, text = 'Number of measurements per mask')
		self.num_meas = Entry(self.params, textvariable = self.num_meas_c)

 		self.avg_delay_c = IntVar()
 		self.avg_delay_c.set(0)
 		self.avg_delay_l = Label(self.params, text = 'Delay between measurements')
		self.avg_delay = Entry(self.params, textvariable = self.avg_delay_c)

 		self.apply_cal_c = BooleanVar()
 		self.apply_cal_c.set(True)
 		self.apply_cal = Checkbutton(self.params, text = 'Apply calibration', variable = self.apply_cal_c)

 		self.averaging_c = BooleanVar()
 		self.averaging_c.set(True)
		self.averaging = Checkbutton(self.params, text = 'Average', variable = self.averaging_c) 		

 		self.caching_c = BooleanVar()
 		self.caching_c.set(True)
 		self.caching = Checkbutton(self.params, text = 'Cache', variable = self.caching_c)

 		self.viewf_c = IntVar()
 		self.viewf_c.set(634)
 		self.viewf_l = Label(self.params, text = 'View frequency')
		self.viewf = Entry(self.params, textvariable = self.viewf_c)

		self.attr_c = StringVar()
		self.attr_c.set('s_db')
		self.attr_l = Label(self.params, text = 'Attribute')
		self.attr = Entry(self.params, textvariable = self.attr_c)
		
		#raster
		self.xlen_c = IntVar()
		self.xlen_l = Label(self.params, text = 'X Length')
		self.xlen = Entry(self.params, textvariable = self.xlen_c)

		self.ylen_c = IntVar()
		self.ylen_l = Label(self.params, text = 'Y Length')
		self.ylen = Entry(self.params, textvariable = self.ylen_c)

		#bar
		self.parts_c = IntVar()

		#all methods
		self.top_frame = Frame(self, bg = 'green')
		self.method_c = StringVar()
		self.method_c.trace('w', self.update)
		self.method_c.set('hadamard')
		Label(self.top_frame, text = 'Imaging method').pack(side = LEFT, padx = 5, pady = 5)
		OptionMenu(self.top_frame, self.method_c, 'hadamard', 'raster', 'bar').pack(side = LEFT, padx = 5, pady = 5)
		self.top_frame.pack(side = TOP, fill = X)


		self.params.pack(side = TOP, fill = 'both', expand = True)

		self.bot_frame = Frame(self, bg = 'yellow')
		
		self.name_c = StringVar()
		Label(self.bot_frame, text = 'Name').pack(side = LEFT, padx = 5, pady = 5)
		Entry(self.bot_frame, textvariable = self.name_c).pack(side = LEFT, pady = 5)

		self.var_c = IntVar()
		self.var_c.set('primary')
		#Label(self.bot_frame, text = 'Mask variation').pack(side = LEFT)
		OptionMenu(self.bot_frame, self.var_c, 'primary', 'inverse', 'both').pack(side = LEFT, padx = 5, pady = 5)
		
		Button(self, bg = 'yellow', text = 'Take Image', command = self.image).pack(side = RIGHT, padx = 5, pady = 5)
		self.bot_frame.pack(side = BOTTOM, fill = X)


	def update(self, n, m, x):
		f = self.method_c.get()

		if f == 'hadamard':
			self.clear_params()
			self.pack_hadamard()
			return

		if f == 'raster':
			self.clear_params()
			self.pack_raster()
			return

		if f == 'bar':
			self.clear_params()
			self.pack_bar()
			return

	def image(self):
		f = self.var_c.get()
		
		if f is 'hadamard':
			self.controller.kind = pro.hadamard(rank = self.rank_c.get(), scale = self.scale_c.get(), varient = self.var_c.get())
			self.controller.cai.hadamard_image(self.controller.kind)

		if f is 'raster':
			self.controller.kind = pro.raster()

		if f is 'bar':
			self.controller.kind = pro.bar()

	def clear_params(self):
		self.scale.grid_forget()
		self.scale_l.grid_forget()
		self.rank.grid_forget()
		self.rank_l.grid_forget()
		self.take.grid_forget()
		self.mask_delay.grid_forget()
		self.mask_delay_l.grid_forget()
		#self.duty.grid_forget()
		self.num_meas.grid_forget()
		self.num_meas_l.grid_forget()
		self.avg_delay.grid_forget()
		self.avg_delay_l.grid_forget()
		# self.apply_cal.grid_forget()
		# self.averaging.grid_forget()
		# self.caching.grid_forget()
		# self.viewf.grid_forget()
		# self.viewf_l.grid_forget()
		# self.attr.grid_forget()
		# self.attr_l.grid_forget()
		self.xlen.grid_forget()
		self.xlen_l.grid_forget()
		self.ylen.grid_forget()
		self.ylen_l.grid_forget()

	def pack_hadamard(self):

		self.scale_l.grid(row = 0, column = 0, padx = 2, pady = 2, sticky = E)
		self.scale.grid(row = 0, column = 1, padx = 2, pady = 2)
		
		self.rank_l.grid(row = 1, column = 0, sticky = E, padx = 2, pady = 2)
		self.rank.grid(row = 1, column = 1, padx = 2, pady = 2)
		
		self.mask_delay_l.grid(row = 2, column = 0, sticky = E, padx = 2, pady = 2)
		self.mask_delay.grid(row = 2, column = 1, padx = 2, pady = 2)
	
		self.num_meas_l.grid(row = 3, column = 0, sticky = E, padx = 2, pady = 2)
		self.num_meas.grid(row = 3, column = 1, padx = 2, pady = 2)
		
		self.avg_delay_l.grid(row = 4, column = 0, sticky = E, padx = 2, pady = 2)
		self.avg_delay.grid(row = 4, column = 1, padx = 2, pady = 2)

		# self.viewf_l.grid(row = 5, column = 0, sticky = E, padx = 2, pady = 2)
		# self.viewf.grid(row = 5, column = 1, padx = 2, pady = 2)

		# self.attr_l.grid(row = 6, column = 0, sticky = E, padx = 2, pady = 2)
		# self.attr.grid(row = 6, column = 1, padx = 2, pady = 2)

		#self.duty.grid()
		
		#self.apply_cal.grid(row = 0, column = 2, sticky = W, padx = 2, pady = 2)
		#self.averaging.grid(row = 1, column = 2, sticky = W, padx = 2, pady = 2)
		#self.caching.grid(row = 2, column = 2, sticky = W, padx = 2, pady = 2)
		#self.take.grid(row = 3, column = 2, sticky = W, padx = 2, pady = 2)
		

	def pack_raster(self):
		return 0

	def pack_bar(self):
		return 0


class View(Frame):
	def __init__(self, parent, controller):

		Frame.__init__(self, parent)
		self.controller = controller

#main
root = GUI()
root.title('Terahertz Coded Aperture Imaging')
root.geometry('700x600')
root.resizable(0,0)
root.mainloop()