# -*- coding: utf-8 -*-
"""
Created on Thu Feb 12 12:29:52 2020

@author: asasson
"""

import sys
sys.path.append('H:\\Python\\l3hlib')
from Adapters.visa import VISAAdapter
from Instruments.instrument import splitResourceID
from Instruments.powsupply import PS
from Radio.radio import Console, Channel, Radio
from Tests.test import Test
import Utilities.Station
import time
import visa


class PowerTune(Test):
	modes = ['NB', 'WB', 'MUOS']
	
	def __init__(self, pm, red, blk, logfile=None):
		super(PowerTune,self).__init__()
		self._name = "PowerTune"
		self._pm = pm
		self._red = red
		self._blk = blk
		self.config()
		self.configPower()
	
	def close(self):
		self._name = None
		self._pm = None
		self._red = None
		self._blk = None
		
		self._tuneNB = None
		self._tuneWB = None
		self._tuneMUOS = None
		self._MUOSreissue = None
		self._timeout = None
	
		self._fp = None
		self._powoffset = None
		self._tol = None
		self._atten = None
		super(PowerTune,self).close()
	
	def __del__(self):
		self.close()
	
	def config(self, tuneNB=True, tuneWB=True, tuneMUOS=True, MUOSreissue=True, timeout=20):
		self._tuneNB = tuneNB
		self._tuneWB = tuneWB
		self._tuneMUOS = tuneMUOS
		self._MUOSreissue = MUOSreissue
		self._timeout = timeout
	
	def configPower(self, fullpower=43, offset=0.14, tol=0.1, attenuation=40):
		self._fp = fullpower
		self._powoffset = offset
		self._tol = tol
		self._atten = attenuation
	
	def configWBTEST(self, mode="WB", param=[3e7, "tx", "conttone", 1, 0]):
		self._blk.send("debug seq verbose off")
		if mode=="MUOS" : self._blk.send("debug seq extra6 8 lb")
		debugcmds = ["debug seq freq {}", 
					"debug seq direction {}", 
					"debug seq testtype conttone", 
					"debug seq datarate 1", 
					"debug seq cutpower 0", 
					"debug seq modemstart"]
		for i,c in debugcmds:
			self._blk.send((c + " lb" if mode=="MUOS" else "").format(param[i]))
			time.sleep(0.1)
			self._blk.flush()
		
		self._blk.flush()
		self._blk.validPrompt()
	
	def fetchStablePower(self, delay = 1, debugOn = False):
		stable = 0
		maxtol = 0.1
		attempts = 0
		maxattempts = 200
		lastpwr = float(self._pm.query("FETC?"))
		while(attempts < maxattempts) :
			time.sleep(delay)
			pwr = float(self._pm.query("FETC?"))
			dev = abs(pwr - lastpwr)/pwr
			if(dev < maxtol) :
				stable += 1
			if(stable == 5) : return pwr
			lastpwr = pwr
	
	def main(self):
		while():
			red.validPrompt()
			blk.validPrompt()
		self._red.send("ascii")
		self.tunetables = ["","",""]
		tune = 20
		if(self._tuneNB):
			cutpwr = 0
			self._red.send("power user 0")
			self._red.send("vulos pre act freq 300")
			self._red.send("vulos pre act trafficmode data")
			self._red.flush()
			self._red.send("radio txpoweroffet nb")
			self.tunetables[0] = self._red.readlines()
			print(self.tunetables[0])
			self._red.send("bert start")
			while cutpwr < 11:
				self._red.send("power user {}".format(cutpwr))
				time.sleep(1)
				tune = self.tune("NB", tune, cutpwr)
				cutpwr += 1
			self._red.send("bert stop")
			self._red.send("radio txpoweroffet save")
		if(self._tuneWB):
			cutpwr = 0
			self._red.flush()
			self._red.send("radio txpoweroffet wb")
			self.tunetables[1] = self._red.readlines()
			self._red.send("bit wide eng")
			time.sleep(10)
			self.configWBTEST()
			while cutpwr < 20:
				self._blk.send("debug seq cutpower {}".format(cutpwr))
				time.sleep(1)
				self.tune("WB", tune, cutpwr)
				cutpwr += 1
			self._red.send("bit wide stop")
			self._red.send("radio txpoweroffet save")
		if(self._tuneMUOS):
			cutpwr = 0
			self._red.flush()
			self._red.send("radio txpoweroffet muos")
			self.tunetables[2] = self._red.readlines()
			self._red.send("bit wide eng")
			time.sleep(10)
			self.configWBTEST("MUOS")
			while cutpwr < 46:
				self._blk.send("debug seq cutpower {} lb".format((cutpwr + 3)))
				time.sleep(1)
				self.tune("MUOS", tune, cutpwr)
				cutpwr += 1
			self._red.send("bit wide stop")
			self._red.send("radio txpoweroffet save")
		
		return self._red.send("vulos pre act trafficmode datavoice")
	
	def tune(self, mode, starttune, cutpower):
		print("*** {} , {} starting with value {}****".format(mode, cutpower, starttune))
		target = self._fp - cutpower - 3
		if(mode == "MUOS" and cutpower == 0):
			target = 39
		print("TARGET: ", target)
		untuned = 1
		tune = starttune
		while untuned:
			if(mode == "NB") :
				self._red.send("radio txpoweroffset NB {} POWER {}".format(tune, cutpower + 3))
			elif(mode == "WB") :
				self._red.send("radio txpoweroffset WB {} POWER {}".format(tune, cutpower + 3))
			elif(mode == "MUOS") :
				self._red.send("radio txpoweroffset MUOS {} POWER {}".format(tune, cutpower + 3))
			else:
				print("Invalid Mode")
			power = self._pm.power()
		print(target, power)
		return power
	
	def spotCheck(self, freq = 30, cutpower = 0):
		pass


MUOSreissue = True
max_attempts = 200
modes = ['NB', 'WB', 'MUOS']


if __name__ == "__main__":
	logfile = open("C:\\Users\\asasson\\Documents\\Logs\\ptune.txt","w")
	logfile.write("Log file\n")
	logfile.flush()
	rm = visa.ResourceManager()
	try:
		addr_ps = "GPIB0::6::INSTR"
		print('Available Instruments: \n\n', rm.list_resources(),'\n\n')
		r = rm.open_resource(addr_ps)
		mm = splitResourceID(r.query('*idn?')[:-1])
		print(mm)
		adptr = VISAAdapter("TestAdapter", r)
		ps =  PS(mm, adptr)
		ps.output_state(0)
		ps.voltage(26)
		time.sleep(1)
		ps.output_state(1)
		
		pm = rm.open_resource('GPIB0::14::INSTR')
	except:
		print("GPIB FAILURE")
		exit(0)
		print("Power Supply Error")
	
	try:
		print(reduut)
	except:
		reduut = Console('RED', 'COM6')
	
	try:
		print(blkuut)
	except:
		blkuut = Console('BLK', 'COM7')
	
	tune = [True, True, True]
	
	test = PowerTune(pm, reduut, blkuut)
	tune.main()
	
	try:
		reduut.close()
		blkuut.close()
	except:
		print("whoops")
