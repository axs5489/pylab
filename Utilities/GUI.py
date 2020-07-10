#
# Serial COM Port terminal program
# 3/19/2019, Arshia Sasson
# This application uses the SerialPort class to implement a GUI serial terminal.
#

import sys
sys.path.append('H:\\Python\\l3hlib')
import console
import time
import _thread
import tkinter as tk
import tkinter.scrolledtext as tkscrolledtext
from tk import *
from tkinter import filedialog
from tkinter import messagebox


class GUI():
	def __init__(self, rcp=None, red=None, blk=None, filepath=None, debugOn=False, debugTime=False):
		self.root = tk.Tk()
		self._width = self.root.winfo_screenwidth()
		self._height = self.root.winfo_screenheight()
		self.root.minsize(width=800, height=600)
		self._frame = Frame(root)
		
		try:
			if(rcp is not None) :
				self.rcp = console("RCP", rcp, filepath, debugOn, debugTime)
			if(red is not None) :
				self.red = console("RED", red, filepath, debugOn, debugTime)
			if(blk is not None) :
				self.blk = console("BLK", blk, filepath, debugOn, debugTime)
		except:
			print("GUI initialization problem")
		
		root.mainloop()
	
	def close():
		self._root = None
		self._width = None
		self._height = None
		self._frame = None
	
	def __del__(self):
		self.close()
		
if __name__ == "__main__":
	example = GUI()