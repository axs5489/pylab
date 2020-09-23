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
		except SerialException:
			print(comport, " already open")
		
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
	
	def readBuffer(self, pub=False):
		if(super().isOpen()) :
			buf = ''
			while self.inWaiting() > 0:
				buf += (self.read(1)).decode()
			if(pub): publish(buf)
			return buf
		return False
	
	def sendCommand(self, cmd):
		return self.write((cmd + '\n').encode('utf-8'))
	
	def send_and_wait(self, cmd, prompt=False):
		self.sendCommand(cmd)
		
		buffer = ""
		found = 0
		while(not prompt and not found):
			output = self.readBuffer()
			buffer += output
			if(output.find(prompt) or buffer.find(prompt)) :
				found = 1
		
		self.postMessage(buffer)
		return found
	
	def validateASCII(response):
		prompts = ["F3", "NORM", "LOAD", "INST", "PRGM"]
		for p in prompts:
			if(response.find(p)):
				if self.debugOn : print("Found {}".format(p))
				return True
		return False

	def validatePrompt(response):
		return validateASCII(response) or response.find('#')
		
	def validPrompt(self, blocking=False):
		buffer = ""
		found = 0
		while(blocking and not found):
			self.sendCommand('\n')
			output = self.readBuffer()
			buffer += output
			if(win.validatePrompt(output)) :
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
		self.sendCommand('startusb', '#')
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
		pass
	
	def close():
		pass
	
	def __del__(self):
		self.close()

class Radio():
	def __init__(self, name=None, comport=None, filepath=None, debugOn=False, debugTime=False):
		pass
		
	def close():
		pass
	
	def __del__(self):
		self.close()


if __name__ == "__main__":
	testcon = console("test",'COM1','C:\\Users\\asasson\\Documents\\Logs\\dbg_console.txt',True,False)