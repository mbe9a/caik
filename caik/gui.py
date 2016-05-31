'''
Alex Arsenovic, Michael Eller, Noah Sauber
UVA THZ CAI
'''

#graphic user interface for caik

from Tkinter import *

#setup window
root = Tk()
root.title("Teraherts Coded Aperture Imaging")
root.geometry("500x500")

label = Label(root, text = "Select a rank ")
label1 = Label(root, text = "Select an imaging technique ")

rank = Entry(root)
x = StringVar()

method = OptionMenu(root, x, "Hadamard", "Raster", "Bar")
run_button = Button(root, text = "Run")

label.grid(row = 0)
label1.grid(row = 1)

rank.grid(row = 0, column = 1)
method.grid(row = 1, column = 1)


run_button.grid(row = 5)



root.mainloop()