# -*- coding: utf-8 -*-
"""
Created on Thu Feb 12 12:29:52 2020

@author: asasson
"""

import sys
sys.path.append('H:\\Python\\l3hlib')
import Radio.radio
from Tests.test import Test
import time
import visa
import Utilities.devmngr


class PowerTune(Test):
	def __init__(devmng = None, logfile=None, debugOn = False):
		super(PowerTune,self).__init__(dm=devmng)
		self._name = "PowerTune"
		self.config()
		self.configPower()
	
	def config(tuneNB=True, tuneWB=True, tuneMUOS=True, MUOSreissue=True, timeout=200):
		self._tuneNB = tuneNB
		self._tuneWB = tuneWB
		self._tuneMUOS = tuneMUOS
		self._MUOSreissue = MUOSreissue
		self._timeout = 200
	
	def configPower(fullpower=43, offset=0.14, tol=0.1, attenutation=40):
		self._fp = fullpower
		self._powoffset = offset
		self._tol = tol
		self._atten = attenuation
	
	def close(self):
		super(PowerTune,self).close()
		self._tuneNB = None
		self._tuneWB = None
		self._tuneMUOS = None
		self._MUOSreissue = None
		
		self._fp = None
		self._powoffset = None
		self._tol = None
		self._atten = None
	
	def __del__(self):
		self.close()
	
	def fetchPower(pm, debugOn = False):
		if debugOn : print("*** FETCH ****")
		pwr = float(power_meter.query("FETC?"))
		if debugOn : print("POWER: ", pwr)
		return pwr
	
	def fetchStablePower(pm, delay = 1, debugOn = False):
		stable = 0
		maxtol = 0.1
		attempts = 0
		maxattempts = 200
		lastpwr = float(power_meter.query("FETC?"))
		while(attempts < maxattempts) :
			time.sleep(delay)
			pwr = float(power_meter.query("FETC?"))
			dev = abs(pwr - lastpwr)/pwr
			if(dev < maxtol) :
				stable += 1
			if(stable == 5) : return pwr
			lastpwr = pwr
	
	def tuneCutPower(pm, rcon, bcon, mode, starttune, cutpower, debugOn = False):
		if debugOn : print("*** {} {} ****".format(mode, cutpower))
		untuned = 1
		tune = starttune
		while untuned:
			if(mode == "NB") :
				red.sendCommand("radio txpoweroffset NB {} POWER {}".format(tune, cutpower + 3))
			elif(mode == "WB") :
				red.sendCommand("radio txpoweroffset WB {} POWER {}".format(tune, cutpower + 3))
			elif(mode == "MUOS") :
				red.sendCommand("radio txpoweroffset MUOS {} POWER {}".format(tune, cutpower + 3))
			else:
				print("Invalid Mode")
			power = fetchPower(pm)
		pass

MUOSreissue = True
max_attempts = 200
modes = ['NB', 'WB', 'MUOS']


if __name__ == "__main__":
	logfile = open("C:\\Users\\asasson\\Documents\\Logs\\ptune.txt","w")
	logfile.write("Log file\n")
	logfile.flush()
	
	try:
		red = console.Console('RED', 'COM6')
		blk = console.Console('BLK', 'COM7')
	except:
		print("COMMS already open")
		exit(0)
		
	try:
		rm = visa.ResourceManager()
		print('Available Instruments: \n\n', rm.list_resources(),'\n\n')
		power_meter = rm.open_resource('GPIB0::14::INSTR')
	except:
		print("GPIB FAILURE")
		exit(0)
	
	attempts = 0
	num_fail = 0
	num_boot_fail = 0
	state = -1
	cutpwr = 0
	inittune = 0
	rcpboot = False
	redboot = False
	timeoff = time.perf_counter()
	lasttime = time.perf_counter()
	while (red.isOpen() and (attempts < max_attempts) and (state > -2)):
		if(state == -1) :
			attempts += 1
			logfile.write("****** Attempts: " + str(attempts))
			red.validPrompt()
			blk.validPrompt()
			red.sendCommand("ascii")
			red.sendCommand("vulos pre act freq 300")
			# red.sendCommand("radio txpoweroffset")
		elif(state == 0 and tuneNB) :
			if debugOn : print("********** Initiating NB TUNE **********")
			if(cutpwr < 11) :
				red.sendCommand("power user {}".format(cutpwr))
				red.validPrompt()
				inittune = tuneCutPower(power_meter, red, blk, "NB", inittune, cutpwr)
				cutpwr +=1
			else:
				state = 3
				red.sendCommand("radio txpoweroffset save")
		elif(state == 1) :
			cutpwr = 0
			red.sendCommand("bit wide eng")
			blk.validPrompt()
			if(tuneWB) :
				if debugOn : print("********** Initiating WB TUNE **********")
				blk.sendCommand("debug seq verbose off")
				blk.sendCommand("debug seq freq 300000000")
				blk.sendCommand("debug seq direction tx")
				blk.sendCommand("debug seq testtype conttone")
				blk.sendCommand("debug seq datarate 1")
				
				state = 2
			else:
				if debugOn : print("********** Skipping WB TUNE **********")
				state = 3
		elif(state == 2 and tuneWB) :
			if debugOn : print("*************** WB TUNE ***************")
			if(cutpwr < 20) :
				blk.sendCommand("debug seq cutpower {}".format(cutpwr))
				blk.sendCommand("debug seq modemstart lb")
				tuneCutPower(power_meter, red, blk, "WB", inittune, cutpwr)
				cutpwr += 1
			else:
				state = 3
				blk.sendCommand("debug seq modemstop")
				red.sendCommand("radio txpoweroffset save")
		elif(state == 3) :
			if(tuneMUOS) :
				if debugOn : print("********* Initiating MUOS TUNE *********")
				if(not tuneWB) : red.sendCommand("bit wide eng")
				blk.validPrompt()
				blk.sendCommand("debug seq verbose off")
				blk.sendCommand("debug seq freq 300000000 lb")
				blk.sendCommand("debug seq direction tx lb")
				blk.sendCommand("debug seq testtype conttone lb")
				blk.sendCommand("debug seq datarate 1 lb")
				blk.sendCommand("debug seq extra6 8 lb")
				cutpwr = 3
				state = 4
			else:
				if debugOn : print("********* Skipping MUOS TUNE *********")
				state = -2
		elif(state == 4 and tuneMUOS) :
			if debugOn : print("************** MUOS TUNE **************")
			if(cutpwr < 50) :
				blk.sendCommand("debug seq cutpower {} lb".format(cutpwr))
				if(MUOSreissue) : blk.sendCommand("debug seq modemstart lb")
				tuneCutPower(power_meter, red, blk, "MUOS", inittune, cutpwr)
				cutpwr += 1
			else:
				state = -2
				blk.sendCommand("debug seq modemstop lb")
				red.sendCommand("radio txpoweroffset save")
	
	try:
		red.close()
		blk.close()
	except:
		print("whoops")
	