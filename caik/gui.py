'''
Alex Arsenovic, Michael Eller, Noah Sauber
UVA THZ CAI
'''

#graphic user interface for caik

from Tkinter import *

#initialize window
root = Tk()
root.title("Teraherts Coded Aperture Imaging")
root.geometry("500x500")

#labels
label = Label(root, text = "Select a rank ")
label1 = Label(root, text = "Select an imaging technique ")

#control variables
x = StringVar()

#widgets
method = OptionMenu(root, x, "Hadamard", "Raster", "Bar")
run_button = Button(root, text = "Run")
rank = Entry(root)

#layout
label.grid(row = 0, sticky = E)
label1.grid(row = 1, sticky = E)
rank.grid(row = 0, column = 1)
method.grid(row = 1, column = 1)
run_button.grid(row = 5)


def run():
	root.mainloop()

def exit():
	root.quit()