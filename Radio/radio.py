# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 14:40:09 2019

@author: asasson
"""

import Utilities.win
from serial import Serial, SerialException
import time


class Console(Serial):
	# Console Modes
	CONSOLE = 'CONSOLE'
	F3 = 'F3' # No WFs Active
	INSTALL = 'INST'
	LOAD = 'LOAD'
	NORM = 'NORM'
	PROGRAM = 'PRGM'
	_ASCII = [F3, NORM, LOAD, INSTALL, PROGRAM]
	
	def __init__(self, name=None, comport=None, filepath=None, debugOn=False, debugTime=False):
		""" Console Constructor
				name: any string (ie, 'RCP')
				comport: 'COMn' string (ie, 'COM21')
				filepath: log file name ('.txt')
				AduSN: Associated Relay ('E0####')
		"""
		self.name = name
		self.debugOn = debugOn
		self.state = -1
		self.attempts = 0
		self.num_bootfail = 0
		self.num_fail = 0
		
		if(comport == None) :
			comport = Utilities.win.findRadioPort()
			if(comport == -1):
				exit(1)
		
		try:
			super().__init__(port=comport,baudrate=115200,timeout=5)
		except SerialException as se:
			print("UNABLE TO OPEN: ", comport)
			print(se)
		
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
		super().close()
	
	def __del__(self):
		self.close()
	
	def read(self, n=1):
		return super().read(n).decode()
	
	def readline(self, pub=False):
		line = []
		for c in self.read():
			line.append(c)
			if c == '\n' or self.inWaiting() == 0:
				return line
	
	def readlines(self, pub=False):
		i = 0
		lines = []
		while self.inWaiting() > 0:
			lines[i] = self.readline(pub)
			i += 1
		return lines
	
	def readBuffer(self, pub=False):
		if(super().isOpen()) :
			buf = ''
			while self.inWaiting() > 0:
				buf += (self.read(1)).decode()
			if(pub): publish(buf)
			return buf
		return False
	
	def write(self, cmd):
		super().write(cmd.encode('utf-8'))
	
	def send(self, cmd):
		if(cmd[-1] is not '\n'):
			cmd += '\n'
		self.write(cmd)
		super.flush()
	
	def send_and_wait(self, cmd, prompt=None):
		self.send(cmd)
		
		buffer = ""
		found = 0
		while(not prompt and not found):
			output = self.readBuffer()
			buffer += output
			if(output.find(prompt) or buffer.find(prompt)) :
				found = 1
		
		self.postMessage(buffer)
		return found
	
	def validatePrompt(self, response, ASCII = False):
		for p in self._ASCII:
			if(response.find(p)):
				if self.debugOn : print("Found {}".format(p))
				return True
		if (not ASCII and response.find('#')):
			return True
		return False

	# def validatePrompt(self, response):
		# return validateASCII(response) or response.find('#')
		
	def validPrompt(self, blocking=False, ASCII = False):
		buffer = ""
		found = 0
		while(blocking and not found):
			self.send('\n')
			output = self.readBuffer()
			buffer += output
			if(win.validatePrompt(output, ASCII)) :
				found = 1
		
		self.publish(buffer)
		return found
	
	def publish(self, msg):
		if self.debugOn : print(msg)
		if(self.logenabled) :
			self.logfile.write("Log file\n")
			self.logfile.flush()

	def startUSB(self):
		driveNumber = -1
		timeout = 10
		# Let's grab a list of all active drive letters
		drivebits = Utilities.win.getDrives()
		self.send('startusb', '#')
		startTime = time.time()
		while time.time()-startTime < timeout:
			time.sleep(2)
			diffDrive = abs(drivebits - win32file.GetLogicalDrives())
			if diffDrive:
				# The difference, log 2, will yield the ordinal
				driveNumber = int(math.log(diffDrive, 2))
				break
		return driveNumber
		
	def ignore(self, t):
		pass
		
	def waitFor():
		pass

class Channel():
	def __init__(self, name=None, redcomport=None, blkcomport=None, filepath=None, debugOn=False, debugTime=False):
		self._name = name
		self.red = Console(redcomport)
		self.blk = Console(blkcomport)
	
	def close():
		pass
	
	def __del__(self):
		self.close()

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
		
	def close():
		pass
	
	def __del__(self):
		self.close()


if __name__ == "__main__":
	testcon = Console("test",'COM6','C:\\Users\\asasson\\Documents\\Logs\\dbg_console.txt',True,False)