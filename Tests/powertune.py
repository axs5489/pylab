# -*- coding: utf-8 -*-
"""
Created on Thu Feb 12 12:29:52 2020

@author: asasson
"""

from Adapters.visa import VISAAdapter
from Instruments.instrument import splitResourceID
from Instruments.powmeter import PowerMeter
from Instruments.powsupply import PS
from Radio.radio import Console, Channel, Radio
from Tests.test import Test
#import Utilities.Station
from math import exp
import time
import visa


class PowerTune(Test):
	modes = ['NB', 'WB', 'MUOS']
	
	def __init__(self, pm, ch, logfile=None):
		super(PowerTune,self).__init__()
		self._name = "PowerTune"
		self._pm = pm
		self._ch = ch
		self._red = ch.red
		self._blk = ch.blk
		self._debug = False
		self.config()
		self.configPower()
		self.calibrate()
	
	def close(self):
		self._name = None
		self._pm = None
		self._ch = None
		self._red = None
		self._blk = None
		self._debug = None
		
		self._tuneNB = None
		self._tuneWB = None
		self._tuneMUOS = None
		self._MUOSreissue = None
		self._timeout = None
	
		self._fp = None
		self._powoffset = None
		self._tol = None
		self._atten = None
		#super(PowerTune,self).close()
	
	def __del__(self):
		self.close()
	
	def calibrate(self):
		self._pm.ch1.freq(300000000)
		print("You need to calibrate the Power Meter Sensor!")
		res = input()
		if(res.upper() != 'N') : self._pm.ch1.calibrate(1)
		print("You need to set the Power Meter attenuator offset!")
		res = input()
		if(res.upper() != 'N') : self._pm.ch1.autoattenuate()
		self._atten = self._pm.ch1.offset()
		print("Offset: ", self._atten)
		print("Power Meter Calibrated!")
		input()
	
	def config(self, tuneNB=True, tuneWB=True, tuneMUOS=True, reissue=True, timeout=20):
		self._tuneNB = tuneNB
		self._tuneWB = tuneWB
		self._tuneMUOS = tuneMUOS
		self._reissue = reissue
		self._timeout = timeout
	
	def configPower(self, fullpower=43, offset=0.12, tol=0.1):
		self._fp = fullpower
		self._powoffset = offset
		self._tol = tol
	
	def configWBTEST(self, mode="WB", f=3e8, d="tx", m="conttone", r="1", c=0):
		self._blk.send("debug seq verbose off")
		if mode=="MUOS" : self._blk.send_and_wait("debug seq extra6 8 lb", '#')
		appnd = " lb" if mode=="MUOS" else ""
		param = [f, d, m, r, c, ""]
		debugcmds = ["debug seq freq {}", 
					"debug seq direction {}", 
					"debug seq testtype {}", 
					"debug seq datarate 1", 
					"debug seq cutpower 0", 
					"debug seq modemstart"]
		for i,c in enumerate(debugcmds):
			cmd = (c + appnd).format(param[i])
			print(cmd)
			self._blk.send_and_wait(cmd, '#')
			time.sleep(0.5)
			self._blk.flush()
		
		print("WBTEST CONFIG")
		self._blk.flush()
		self._blk.send_and_wait("\n", "#")
	
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
		unready = 1
		self._ch.AsciiMode()
		self.tunetables = ["","",""]
		while(unready):
			self._red.flush()
			self._blk.flush()
			self._pm.ch1.power()
			time.sleep(1)
			if(self._red.isOpen() and self._blk.isOpen()) : unready = 0
		
		if(self._tuneNB):
			tune = 15
			cutpwr = 0
			self.mode = "NB"
			self._red.send("power user 0")
			self._red.send("vulos pre act freq 300")
			self._red.send("vulos pre act trafficmode data")
			self._red.flush()
			self._red.send("RADIO TXPOWEROFFSET NB")
			time.sleep(1)
			self.tunetables[0] = self._red.flush()
			print(self.tunetables[0])
			self._red.send("bert start")
			while cutpwr < 11:
				self._red.send_and_wait("power user {}".format(cutpwr), "POWER USER")
				self._red.send_and_wait("\n", '>')
				tune = self.tune("NB", tune, cutpwr)
				self._red.flush()
				cutpwr += 1
			self._red.send_and_wait("bert stop", '>')
			self._red.send_and_wait("RADIO TXPOWEROFFSET SAVE", '>')
		if(self._tuneWB):
			tune = 15
			cutpwr = 0
			self.mode = "WB"
			self._red.flush()
			self._red.send("RADIO TXPOWEROFFSET WB")
			time.sleep(1)
			self.tunetables[1] = self._red.flush()
			self._red.send("bit wide eng")
			time.sleep(10)
			self._blk.waitFor("#")
			self.configWBTEST()
			while cutpwr < 20:
				self._blk.send_and_flush("debug seq cutpower {}".format(cutpwr))
				self._blk.send_and_wait("\n", '#')
				tune = self.tune("WB", tune, cutpwr)
				self._red.flush()
				cutpwr += 1
			self._blk.send_and_wait("debug seq modemstop", '#')
			self._red.send_and_wait("bit wide stop", '>')
			self._red.send_and_wait("RADIO TXPOWEROFFSET SAVE", '>')
		if(self._tuneMUOS):
			tune = 15
			cutpwr = 0
			self.mode = "MUOS"
			self._red.flush()
			self._red.send("RADIO TXPOWEROFFSET MUOS")
			time.sleep(1)
			self.tunetables[2] = self._red.flush()
			self._red.send("bit wide eng")
			time.sleep(10)
			self._blk.waitFor("#")
			self.configWBTEST("MUOS")
			while cutpwr < 46:
				self._blk.send_and_flush("debug seq cutpower {} lb".format((cutpwr + 3)))
				self._blk.send_and_wait("debug seq modemstart lb", "#")
				self._blk.flush()
				tune = self.tune("MUOS", tune, cutpwr)
				self._red.flush()
				cutpwr += 1
			self._blk.send_and_flush("debug seq modemstop lb")
			self._red.send_and_wait("bit wide stop", '>')
			self._red.send_and_wait("RADIO TXPOWEROFFSET SAVE", '>')
		return self._red.send("vulos pre act trafficmode datavoice")
	
	def stop(self):
		if(self.mode == "NB"):
			reduut.send("bert stop")
		else:
			blkuut.send("debug seq modemstop")
			reduut.send("bit wide stop")
	
	def tune(self, mode, tune, cutpower):
		if(self._debug) : print("*** {} , {} starting with value {}****".format(mode, cutpower, tune))
		if(mode.upper() in ["NB", "WB", "MUOS"]):
			self._red.send("RADIO TXPOWEROFFSET {} {} POWER {}".format(mode, tune, cutpower + 3))
			target = round(self._fp + self._powoffset - cutpower - 3, 2)
			if(mode == "MUOS" and cutpower == 0):
				target = 39 + self._powoffset
			print("TARGET: ", target)
			fine = 0
			jalim = 0.06 * (50 - target)# * (50 - target)
			jadelta = 0.3 if target < 10 else 0.01*(46 - target)		# Linear
			#jadelta = 0.3 if target < 10 else 0.4*exp( -0.047*target)		# Exponential
			tried = []
			last = [tune, target - self._pm.powerStable()]
			print('loop reached')
			while True:
				if(not fine and tune in tried):
					jalim = 2*jalim
				tried.append(tune)
				cmd = "RADIO TXPOWEROFFSET {} {} POWER {}".format(mode, tune, cutpower + 3)
				self._red.send(cmd)
				if(mode == "WB" and self._reissue) : self._blk.send_and_wait("debug seq modemstart", '#')
				if(mode == "MUOS" and self._reissue) : self._blk.send_and_wait("debug seq modemstart lb", '#')
				time.sleep(0.5)
				power = self._pm.powerStable()
				if(self._debug) : print(cmd, '\t', power)
				dif = target - power
				cur = [tune, dif]
				if(abs(dif) > 15):				# Something's wrong
					print("Aborting {} cutpower {} tune {}".format(mode, cutpower, tune))
					if(mode == "NB"):
						self._red.send("bert stop")
					else:
						self._red.send("bit wide stop")
					return
				elif(abs(dif) > jalim):			# Jump around
					tune += int(dif/jadelta)		# + Underpowered / - Overpowered
					fine = 0
				elif(fine == 2):
					break
				else:							# Fine tune
					if(dif > 0):
						if(last[1] < 0 and fine):
							if(abs(dif) > abs(last[1])) : tune = last[0]
							fine = 2
						else:
							tune += 1
							fine = 1
					elif(dif < 0):
						if(last[1] > 0 and fine):
							if(abs(dif) > abs(last[1])) : tune = last[0]
							fine = 2
						else:
							tune -= 1
							fine = 1
					else:
						break
					#fine = 1
				#last2 = last
				last = cur
			print("FINAL: ", power)
			return tune
		else:
			print("Unsupported Mode")
	
	def spotCheck(self, freq = 30, cutpower = 0):
		pass



addr_pm = "GPIB0::13::INSTR"
addr_ps = "GPIB0::6::INSTR"
redcom = "COM6"
blkcom = "COM7"
modes = ['NB', 'WB', 'MUOS']


if __name__ == "__main__":
	logfile = open("C:\\Users\\asasson\\Documents\\Logs\\ptune.txt","w")
	logfile.write("Log file\n")
	logfile.flush()
	rm = visa.ResourceManager()
	try:
		print('Available Instruments: \n\n', rm.list_resources(),'\n\n')
		r = rm.open_resource(addr_ps)
		mm = splitResourceID(r.query('*idn?')[:-1])
		print(mm)
		adptr = VISAAdapter("TestAdapter", r)
		ps =  PS(mm, adptr)
		#ps.output_state(0)
		ps.voltage(26)
		time.sleep(1)
		ps.output_state(1)
		
		r = rm.open_resource(addr_pm)
		mm = splitResourceID(r.query('*idn?')[:-1])
		print(mm)
		adptr = VISAAdapter("TestAdapter", r)
		pm =  PowerMeter(mm, adptr)
		#time.sleep(30)
	except:
		print("GPIB FAILURE")
		exit(0)
		print("Power Supply Error")
	
	try:
		reduut = Console('RED', redcom)
	except:
		reduut.close()
		reduut = Console('RED', redcom)
	
	try:
		blkuut = Console('BLK', blkcom)
	except:
		reduut.close()
		blkuut = Console('BLK', blkcom)
	
	try:
		if(reduut.isOpen() and blkuut.isOpen()):
			print("Serial ports opened")
			ch = Channel("PT Channel", reduut, blkuut)
			ch.flush()
			
			tune = PowerTune(pm, ch)
			#			NB     WB	MUOS, reissue, timeout
			tune.config(True, True, False, True, 10)	#MUOS does not work yet!
			tune._debug = True
			print("Configured and Running PowerTune")
			tune.main()
	except Exception as e:
		print(e)
		tune.stop()
		ch.close()
	
	try:
		reduut.close()
		blkuut.close()
	except:
		print("whoops")
