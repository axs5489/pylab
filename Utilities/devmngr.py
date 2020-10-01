# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 13:26:43 2020

@author: asasson
"""
from collections import defaultdict
from Adapters.visa import VISAAdapter
from Instruments import Adu2xx
from Instruments.audiomod import AudioAnalyzer
from Instruments.dmm import DMM
from Instruments.fireberd import FireBERD
from Instruments.freqcount import FreqCounter
from Instruments.generators import SigGen, ArbGen
from Instruments.instrument import splitResourceID
from Instruments.gps import GSG
from Instruments.netan import NetAnalyzer
from Instruments.powmeter import PowerMeter#, DualPowerMeter
from Instruments.powsupply import PS
from Instruments.rfswitch import rfSW
from Instruments.scope import Oscilloscope
from Instruments.specan import SpecAnalyzer
import Radio.radio
from Radio.radio import Console, Channel, Radio
import Utilities.win
import Utilities.config
import time
import visa

adu_types = ["ADU"]
com_types = ["CON", "STP", "RCP", "RED", "BLK", "RUT", "BUT", "RFSW"]
res_types = [AudioAnalyzer, ArbGen, DMM, FireBERD, FreqCounter, NetAnalyzer, 
			 PowerMeter, PS, rfSW, SigGen, GSG, SpecAnalyzer, Oscilloscope]


class Station():
	def __init__(self, logfile=None, debugOn=False):
		""" Console Constructor
			name: any string (ie, 'RCP')
			logfile: log file name ('.txt')
			"""
		self._debugOn = debugOn
		self._savedconfig = Utilities.config.get()
		self._adus = []
		self._consoles = defaultdict(list)
		self._instruments = defaultdict(list)
		self._drives = Utilities.win.getDrives()
		self._ports = Utilities.win.listSerialPorts()
		if(self._debugOn):
			print('Configuration: ', self._savedconfig)
			print('Drives: ', self._drives)
			print('Ports : ', self._ports)
		self._hardreset = False
		self._rm = visa.ResourceManager()
		#try:
		self.autoinit()
		if self._debugOn : print('Opened Instruments: \n\n', self._instruments,'\n\n')
#			self._active = True
# 			if(self._devices["ADU"] != None) :	#Open Relay Box, if requested
# 				self._hardreset = True
# 				self.Adu218 = Adu2xx.Adu218(sn="E06449")
# 				if(self.Adu218 != None ) :
# 					print ("Found ADU200 device")
# 				else :
# 					print ("ADU200 device not found")
# 		except Exception as e:
# 			print("Unable to initialize Dev Manager")
# 			print(e)
# 			input()
# 			for attr in dir(self):
# 				print(attr, getattr(self, attr))
# 			self.close()
	
	def close(self):
		x= input("Save configuration (Y/n): ")
		if(x.upper() == 'Y'):
			Utilities.config.save(self._config)
		self._config = None
		self._savedconfig = None
		self._adus = None
		self._consoles = None
		self._instruments = None
		self._drives =None
		self._hardreset = None
		self._ports = None
		self._rm = None
		self._resources = None
		self._visaresources = None

	def __del__(self):
		self.close()

	def autoinit(self):
		self._visaresources = self._rm.list_resources()
		if self._debugOn : print('VISA: \n\n', self._visaresources,'\n\n')
		self._resources = defaultdict(list)
		for res in self._visaresources:
			visacon = self._resources["VISA"]
			if(res not in visacon):
				if(res.find("GPIB") or res.find("GPIB")):
					print(res)
				self._resources["VISA"].append(res)
		for typ,addr in self._savedconfig.items():
			print(typ, "  ", addr)
			if(typ in adu_types):
				self._resources["ADU"].append(addr)
			elif(typ in com_types):
				self._resources["CON"].append(addr)
			else:
				self._resources["VISA"].append(addr)
		if self._debugOn : print('\nConfigured: \n\n', self._resources,'\n\n')
		self.init_resources()
		if self._debugOn :
			print('Available Instruments: \n\n', self._instruments,'\n\n')
			for instr in self._instruments:
				print('INSTRUMENT: ', instr,'\n\n', dir(instr),'\n\n')
	
	def init_resources(self):
		"""
		Prints the available resources, and returns a list of VISA resource names
			#prints (e.g.)
				#0 : GPIB0::22::INSTR : Agilent Technologies,34410A,******
				#1 : GPIB0::26::INSTR : Keithley Instruments Inc., Model 2612, *****
			dmm = Agilent34410(resources[0])
		"""
		if self._debugOn : print('INITIALIZING')
		for typ, reslist in self._resources.items():
			if(typ == "ADU"):
				self._hardreset = True
				Adu218 = Adu2xx.Adu218(sn="E06449")
				if(Adu218 != None ) :
					print ("Found ADU200 device")
					self._adus.append(Adu218)
				else :
					print ("ADU200 device not found")
			elif(typ == "CON"):
				pass
			elif(typ == "VISA"):
				for instr in reslist:
					try:
						res = self._rm.open_resource(instr)
						try:
							idn = res.query('*idn?')[:-1]
							mm = splitResourceID(idn)
							resadptr = VISAAdapter(mm[1], res)
							if self._debugOn : print("\t", instr, ":", idn)
							for icls in res_types:
								sup = icls.checkSupport(mm[1])
								if(sup):
									self._instruments[sup].append(icls(mm,resadptr))
						except visa.Error:
							idn = "Not known"
					except visa.VisaIOError as e:
						print(instr, ":", "Visa IO Error: check connections")
						print(e)
			else:
				print("What the hell is this?")
		return True

	def addConsole(self, name, addr):
		if(name.find("RED") or name.find("RCR")) :
			self.active[name] = None
		elif(name.find("BLK") or name.find("RCR")) :
			pass
		else:
			print("What is this COM Port? ", name, addr)
	
	def addDevice(self, name, addr):
		pass
	
	def addInstrument(self, name, addr):
		pass
	
	def getDevice(self, devtype, name):
		""" Get Device
			devtype: supports 'ADU', 'EQU', 'RAD'
			name: any string (ie, 'E06449', 'RCP')
			"""
		if(self._device.has_key(devtype)) :
			if(self._device[devtype].has_key(name)) :
				return self._device[devtype][name]
			if self._debugOn : print("Not an active device")
			return -1
		
		if self._debugOn : print("Not a supported device type")
		return -2

	def getInstrument(self, name, addr):
		pass

	def delDevice(self, name, addr):
		pass

	def delInstrument(self, name, addr):
		pass

	def reset(self):
		for i in self._instruments:
			i.recover(True)
			i.beep()
			time.sleep(1)

	def setState(self, st):
		self.state = st
		return self.update()
	
	def update(self):
		if(self.state == -2) :
			self.close()
		elif(self.state == -1) :
			self.attempts += 1
			self.logfile.write("****** Attempts: " + str(self.attempts))
			print("****** Attempts: ",str(self.attempts))
			print("****** Fails: ",str(self.num_fail))
			if(self.hardreset) :
				self.Adu218.closeRelay(0)
				time.sleep(2)
				self.Adu218.openRelay(0)
			else:
				self.Tx.reset_input_buffer()
				self.Tx.reset_input_buffer()
				self.Rx.flush()
				self.Rx.flush()
				self.Tx.write(b'ascii\r')
				#time.sleep(1)
				self.Tx.write(b'reset\r')
			self.timeoff = time.perf_counter()
			if self.debugTime : print(self.timeoff)
			time.sleep(10)
			while((not self.reset_type) and self.Tx.in_waiting) :
				rcpbuf = self.readBuffer()
				self.postMessage(rcpbuf)
			self.state = 0
			self.boot = False
			time.sleep(10)
		elif(self.state == 0) :
			self.sendCommandWait("\n","#")
		elif(self.state == 1) :
			pass


if __name__ == "__main__":
	station = Station(debugOn=True)
	#del station