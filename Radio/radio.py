# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 14:40:09 2019

@author: asasson
"""

import Utilities.win
from Utilities.SerialPort import SerialPort
#from WF import Waveform, VULOS
import re
from serial import Serial
import time


class Console():
	# Console Modes
	CONSOLE = 'CONSOLE'
	BIT = "BIT"
	F3 = 'F3' # No WFs Active
	INSTALL = 'INST'
	LOAD = 'LOAD'
	NORM = 'NORM'
	PROGRAM = 'PRGM'
	_ASCII = [">", F3, NORM, LOAD, INSTALL, PROGRAM]
	
	def __init__(self, name=None, comport=None, baud=115200, asyncr=False, filepath=None, debugOn=False):
		""" Console Constructor
				name: any string (ie, 'RCP')
				comport: 'COMn' string (ie, 'COM21')
				baud: the baud rate to use
				async: (T/F) use an asynchronous background thread for all reads
				filepath: log file name ('.txt')
				AduSN: Associated Relay ('E0####')
		"""
		self._debugOn = debugOn
		
		if name:
			self._name = name
		else:
			self._name = comport
		
		try:
			if(comport == None) :
				print("Let's find a COM Port")
				comport = Utilities.win.findRadioPort()
			if(comport == -1):
				print("We screwed up somewhere")
			elif(isinstance(comport, SerialPort)):
				print("Using this SerialPort object")
				self.handle = comport
			elif(isinstance(comport, str)):
				print("Starting new SerialPort")
				self.handle = SerialPort(name, comport, baud)
			else:
				print("What is this?")
		except Exception as se:
			print("UNABLE TO OPEN: ", comport)
			print(se)
		self.port = comport
		
		#Open log file, if requested
		self.logenabled = False
		if(filepath != None) :
			self.logfile = open(filepath,"w")
			self.logfile.write("Log file\n")
			self.logfile.flush()
			self.logenabled = True
		
		self.boot = False
		self.timeoff = time.perf_counter()
		self.lasttime = time.perf_counter()
	
	def close(self):
		if self.isOpen():
			self.handle.close()
	
	def __del__(self):
		self.close()
	
	def isOpen(self):
		if hasattr(self,'handle'):
			return self.handle.handle.isOpen()
	
	def flush(self):
		return self.handle.flush()
		
	def readline(self, pub=False):
		return self.handle.recv().strip()
	
	def readlines(self, pub=False):
		lines = []
		while self.handle.handle.inWaiting() > 0:
			lines.append(self.readline(pub))
			time.sleep(0.05)
		return lines
	
	def write(self, cmd = ""):
		self.handle.send(cmd)
	
	def send(self, cmd = ""):
# 		if(cmd =="" or cmd[-1] is not '\n'):
# 			cmd += '\n'
		self.write(cmd)
	
	def send_and_flush(self, cmd = ""):
		self.send(cmd)
		return self.flush()
	
	def send_and_wait(self, cmd = "", prompt="", timeout = 5, useRegex=False, caseSensitive=False):
		self.send(cmd)
		return self.handle.waitFor(prompt, timeout, False, useRegex, caseSensitive)
	
	def waitFor(self, waitStr = "#"):
		return self.handle.waitFor(waitStr, 10, False)

	# def validatePrompt(self, response):
		# return validateASCII(response) or response.find('#')
	
	def publish(self, msg):
		if self.debugOn : print(msg)
		if(self.logenabled) :
			self.logfile.write("Log file\n")
			self.logfile.flush()

	def startUSB(self, timeout = 10):
		driveNumber = -1
		
		# Let's grab a list of all active drive letters
		old = Utilities.win.getDrives()
		startTime = time.time()
		while time.time()-startTime < timeout:
			self.send('stopusb', '#')
			time.sleep(0.5)
			old = Utilities.win.getDrives()
			self.send('startusb', '#')
			time.sleep(1)
			new = Utilities.win.getDrives()
			for d in old:
				new.remove(d)
			if len(new) == 1:
				driveNumber = new[0]
		return (driveNumber, Utilities.win.getDriveVolumeName(driveNumber))

class Channel():
	def __init__(self, name=None, redcomport=None, blkcomport=None, filepath=None, debugOn=False, debugTime=False):
		self._name = name
		self.serial = {}
		if(isinstance(redcomport, Console)):
			self.red = redcomport
		elif(isinstance(redcomport, str) or isinstance(redcomport, SerialPort)):
			self.red = Console(redcomport)
		else:
			print(name, " doesn't have a red side!")
		
		if(isinstance(blkcomport, Console)):
			self.blk = blkcomport
		elif(isinstance(blkcomport, str) or isinstance(blkcomport, SerialPort)):
			self.blk = Console(blkcomport)
		else:
			print(name, " doesn't have a black side!")
		
		if self.blk:
			self.serial['BLK'] = self.blk
		if self.red:
			self.serial['RED'] = self.red
			self.serial['ASCII'] = self.red # ASCII uses the RED port
	
	def close(self):
		if self.blk.isOpen():
			self.blk.close()
		if self.red.isOpen():
			self.red.close()
	
	def __del__(self):
		self.close()
	
	def isOpen(self):
		return self.red.isOpen() or self.blk.isOpen()

	def clean(self):
		self.ProgMode()
		self.serial['ASCII'].send_and_wait('CLEAN', '>', 5)
		return self.NormalMode()
	
	def flush(self):
		return self.red.flush()
		return self.blk.flush()

	def _ConfigurePort(self,port):
		""" """
		if port not in self.serial:
			print('No \'%s\' Port. Valid Ports are: %s'%(port,self.serial.keys()))
		if port == 'ASCII':
			self.AsciiMode()
		elif port == 'RED':
			self.ExitAscii()

	################

	def NormalMode(self,timeout=30):
		if self.GetMode() != Console.NORM:
			try:
				self.serial['ASCII'].send_and_wait('norm','NORM>|F3', timeout, useRegex=True)
			except:
				print('Error Entering Normal Mode')
		return Console.NORM

	def ProgMode(self):
		if self.GetMode() != Console.PROGRAM:
			self.AsciiMode()   #force ascii mode
			try:
				self.serial['ASCII'].send_and_wait('prog','PRGM>', 30)
			except:
				print('Error Entering Program Mode')
		return Console.PROGRAM

	def AsciiMode(self):
		mode = self.GetMode()
		if mode == Console.CONSOLE:
			try:
				self.serial['RED'].send_and_wait('ascii', '>', 5)
			except:
				print('Error Entering ASCII Mode')
		return mode

	def ExitAscii(self):
		mode = self.GetMode()
		if mode == Console.NORM or mode == Console.F3 or mode == Console.PROGRAM or mode == Console.INSTALL or mode == Console.LOAD:
			try:
				self.serial['ASCII'].send_and_wait('exit', '#', 5)
			except:
				print('Error Exiting ASCII Mode')
		return Console.CONSOLE

	############################################################################
	
	def CheckAscii(self):
		return self.GetMode() != Console.CONSOLE

	def CheckNormalMode(self):
		return self.GetMode() == Console.NORM

	def CheckProgMode(self):
		return self.GetMode() == Console.PROGRAM

	def CheckInstallMode(self):
		return self.GetMode() == Console.INSTALL

	def CheckLoadMode(self):
		return self.GetMode() == Console.LOAD

	def GetMode(self):
		if 'RED' not in self.serial:
			# if no RED port, always assume CONSOLE
			self.currentMode = Console.CONSOLE
			return self.currentMode
		while True:
			ret = self.red.send_and_wait('\n',"NORM>|F3>|PRGM>|INST>|LOAD>|#", 1, True, False)
			if not ret: 
				self.currentMode = None
				print('Error Getting ASCII Mode')
			elif ret.find('NORM>')>=0: self.currentMode = Console.NORM
			elif ret.find('F3>')>=0: self.currentMode = Console.F3
			elif ret.find('PRGM>')>=0: self.currentMode = Console.PROGRAM
			elif ret.find('INST>')>=0: self.currentMode = Console.INSTALL
			elif ret.find('LOAD>')>=0: self.currentMode = Console.LOAD
			elif ret.find('BIT>')>=0: self.currentMode = Console.BIT
			elif ret.find('#')==0 or ret.find('/tmp #')==0 or ret.find('~ #')==0 or "/tmp #" in ret: 
				# make sure the # prompt is at the beginning of the line before deciding this is CONSOLE
				self.currentMode = Console.CONSOLE
			elif ret.find('#')>=0: 
				# got a spurious '#' character, probably from a debug print... so ignore and retry
				continue
			else: 
				self.currentMode = None
				raise Exception('Got Invalid ASCII Mode: %s'%ret)
			break
		return self.currentMode

class Radio():
	def __init__(self, name=None, comport=None, filepath=None, debugOn=False, debugTime=False):
		self._name = name
		if isinstance(comport,list):
			self.rcp = Console(name + " RCP", comport[0])
			self.ch1 = Channel(name + " CH1", comport[1], comport[2])
			self.ch2 = Channel(name + " CH2", comport[3], comport[4])
		elif isinstance(comport,dict):
			self.rcp = Console(name + " RCP", comport["RCP"])
			self.ch1 = Channel(name + " CH1", comport["C1R"], comport["C1B"])
			self.ch2 = Channel(name + " CH2", comport["C2R"], comport["C2B"])
		else:
			print("RADIO ERROR! Give me something to work with")
		
		self.channels = [self.rcp, self.ch1, self.ch2]
		self.comports = [self.rcp, self.ch1.red, self.ch1.blk, self.ch2.red, self.ch2.blk]
		
	def close(self):
		for p in self.comports:
			if(p.isOpen()):
				p.close()
		print("Closing Radio " + self._name)
		self._name = None
	
	def __del__(self):
		self.close()


class atomic:
	"""
	Function decorator to decorate any function that runs console commands that need to be executed atomically
	This decorator will automatically lock the serial device before calling the decorated function and then release
	the lock after the function runs

	Example:

		@atomic('ASCII')
		def Configure(self, **kwargs):
			self.console.SendCmd(...)
			self.console.SendCmd(...)
			self.console.SendCmd(...)

	.. NOTE::
	   Do not use the @atomic decorator on a function that contains a lot of non-serial device, time intensive
	   processes.  This decorator will hold the serial device lock until the function execution is completed and will block
	   other threads from gaining access to the device.  Use console.lock() and console.release() instead.
	"""
	def __init__(self, port):
		"""
		Args:
			port(str): console port name (ASCII, RED, BLK, etc)
		"""
		self.port = port

	def __call__(self, func):
		"""
		Args:
			func: This is the function that is getting wrapped by the decorator
		"""
		def wrapper(inst, *args, **kwargs):
			"""
			This is the wrapper function.  In here, we'll acquire the serial device lock for the correct
			port, run the target function, and then release the lock
			Args:
				inst:   this is the instance object of the caller method
				*args:  target function argument
				**kwargs: target function keyword arguments
			"""
			self.__name__ = func.__name__
			self.__doc__ = func.__doc__

			inst.console.lock(self.port)  # lock the console serial device
			try:
				func(inst, *args, **kwargs)	 # run the target function (all console writes will now be atomic)
			except Exception:
				inst.console.release(self.port)
				raise
			inst.console.release(self.port)   # release the console serial device lock
		return wrapper


if __name__ == "__main__":
	testcon = Console("test",'COM6','C:\\Users\\asasson\\Documents\\Logs\\dbg_console.txt',True,False)