# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 13:47:03 2019

@author: asasson
"""
import sys
sys.path.append('H:\\Python\\axslib')
sys.path.append('H:\\Python\\l3hlib')
import Radio.radio

class MCMP():
	__ident__ = "158"
	__name__ = "MCMP"
	
	def __init__(self, comport):
		self.RCP = Radio.radio.Console()
		self.CH1 = Manpack()
		self.CH2 = Manpack()

class Manpack(Radio):
	def key(self):
		self.sendCommandWait('debug seq modemstart', '#')

	def unkey(self):
		self.sendCommandWait('debug seq modemstop', '#')
	
	def enable_TSM(self, bool):
		if bool:
			self.sendCommandWait('spiDebug 2 69 A4', '#')
	
	def enable_digital_IF_fixed_gain(self, bool):
		if bool:
			self.sendCommandWait('poke -a0x20200002 -w2 0xCE80', '#')
		else:
			self.sendCommandWait('poke -a0x20200002 -w2 0xCE10', '#')
		
	def configWB(self, freq, direction=None, type=None, coded=None, pdu=None,
					wband=None, rband=None, datarate=None, tsmSpecial=None):
		
		self.sendCommandWait('debug seq freq ' + str(freq), '#')
		
		if not direction == None:
			self.sendCommandWait('debug seq direction ' + direction, '#')
		
		if not type == None:
			self.sendCommandWait('debug seq testtype ' + type, '#')
		
		if not coded == None:
			if coded:
				self.sendCommandWait('debug seq uncoded 0', '#')
			else:
				self.sendCommandWait('debug seq uncoded 1', '#')
		
		if not pdu == None:
			self.sendCommandWait('debug seq pdu ' + str(pdu), '#')
		
		if not wband == None:
			self.sendCommandWait('debug seq wband ' + wband, '#')
		
		if not rband == None:
			self.sendCommandWait('debug seq rband ' + rband, '#')
		
		if not datarate == None:
			self.sendCommandWait('debug seq datarate ' + str(datarate), '#')
		
		if not tsmSpecial == None:
			if tsmSpecial:
				self.sendCommandWait('debug seq direction tx', '#')
				self.enable_digital_IF_fixed_gain(True)
				# Disable the keyline.  This is a new function not implemented in the released MFPGA.
				self.sendCommandWait('poke -a0x20c000e4 -w2 0x8000', '#')
			else:
				self.enable_digital_IF_fixed_gain(False)
	
	def configAGC(self, manual, feGainHex, ifGainHex):
		if manual:
			# self.sendCommandWait('debug dvcwdsp fpoke 0x89 0x0020', '#')
			# self.sendCommandWait('debug dvcwdsp fpoke 0x96 ' + feGainHex, '#')
			# self.sendCommandWait('debug dvcwdsp fpoke 0x97 ' + ifGainHex, '#')
			self.sendCommandWait('debug dvcwdsp fpoke 0x8F ' + feGainHex, '#')
			self.sendCommandWait('debug dvcwdsp fpoke 0x9B ' + ifGainHex, '#')