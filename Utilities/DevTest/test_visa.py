# -*- coding: utf-8 -*-
"""
Created on Tue May 12 17:36:17 2020

@author: asasson
"""

from Adapters.visa import VISAAdapter
from Instruments.audiomod import AudioAnalyzer
from Instruments.dmm import DMM
from Instruments.fireberd import FireBERD
from Instruments.freqcount import FreqCounter
from Instruments.generators import SigGen, ArbGen
from Instruments.gps import GSG
from Instruments.instrument import splitResourceID
from Instruments.netan import NetAnalyzer
from Instruments.powmeter import PowerMeter#, DualPowerMeter
from Instruments.powsupply import PS
from Instruments.rfswitch import rfSW
from Instruments.scope import Oscilloscope
from Instruments.specan import SpecAnalyzer
from Utilities import devmngr, win
import visa


instruments = [AudioAnalyzer, ArbGen, DMM, FireBERD, FreqCounter, NetAnalyzer, 
			 PowerMeter, PS, rfSW, SigGen, GSG, SpecAnalyzer, Oscilloscope]
addr_cnt = "GPIB0::14::INSTR"
addr_dmm = None#"GPIB0::7::INSTR"
addr_pm = "GPIB0::13::INSTR"
addr_ps = "GPIB0::6::INSTR"
addr_sa = "GPIB0::18::INSTR"
addr_list = [addr_dmm,
			addr_cnt,
			addr_pm,
			addr_ps,
			addr_sa
			 ]

res = {}
rm = visa.ResourceManager()
print(rm.list_resources())
print(win.listSerialPorts())

for addr in addr_list:
	if(addr is not None):
		try:
			r = rm.open_resource(addr)
			mm = splitResourceID(r.query('*idn?')[:-1])
			print(mm)
			for cl in instruments:
				sup = cl.checkSupport(mm[1])
				if(sup):
					adptr = VISAAdapter("TestAdapter", r)
					instr =  cl(mm, adptr)
					res[addr] = [mm, adptr, instr]
		except:
			print("GPIB Error at ", addr)

print("\nResources:\n")
for k,v in res.items():
	print(k)
	if(k == addr_cnt):
		cnt = res[k][2]
	elif(k == addr_dmm):
		dmm = res[k][2]
	elif(k == addr_pm):
		pm = res[k][2]
	elif(k == addr_ps):
		ps = res[k][2]
	elif(k == addr_sa):
		sa = res[k][2]
	print(v[0])
	for i in instruments:
		print(i.checkSupport(v[0][1]))
