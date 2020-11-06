# -*- coding: utf-8 -*-
"""
Created on Tue May 12 17:36:17 2020

@author: asasson
"""

from Adapters.visa import VISAAdapter
from Instruments.audiomod import AudioAnalyzer, ModulationAnalyzer
from Instruments.dmm import DMM
from Instruments.fireberd import FireBERD
from Instruments.freqcount import FreqCounter
from Instruments.generators import SigGen, ArbGen
from Instruments.gps import GSG
from Instruments.instrument import splitResourceID
from Instruments.netan import NetAnalyzer, HP4396
from Instruments.powmeter import PowerMeter#, DualPowerMeter
from Instruments.powsupply import PS, LambdaPS, XantrexPS
from Instruments.rfswitch import rfSW
from Instruments.scope import DSO, MSO
from Instruments.specan import SpecAnalyzer
from Radio.radio import Console, Channel, Radio
from Utilities import devmngr, win
import visa


instruments = [AudioAnalyzer, ArbGen, DMM, FireBERD, FreqCounter, ModulationAnalyzer, NetAnalyzer, HP4396, 
			PowerMeter, PS, LambdaPS, XantrexPS, DSO, MSO, rfSW, SigGen, GSG, SpecAnalyzer]
addr_cnt = "GPIB0::14::INSTR"
addr_dmm = "GPIB0::7::INSTR"
addr_na = "GPIB0::17::INSTR"
addr_pm = "GPIB0::13::INSTR"
addr_ps2 = "GPIB0::5::INSTR"
addr_ps = "GPIB0::6::INSTR"
addr_sa = "GPIB0::18::INSTR"
addr_scp = 'USB0::0x0957::0x1755::MY48260116::INSTR'
addr_list = [#addr_cnt,
			#addr_dmm,
			addr_na,
			addr_pm,
			addr_ps,
			#addr_ps2,
			addr_sa,
			addr_scp
			 ]

res = {}
rm = visa.ResourceManager()
print(rm.list_resources())
print(win.listSerialPorts())

for addr in addr_list:
	if(addr is not None):
		try:
			r = rm.open_resource(addr)
			idn = r.query('*idn?')[:-1]
			if(idn == ''):
				idn = r.query('ID?')
			mm = splitResourceID(idn)
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
	elif(k == addr_na):
		na = res[k][2]
	elif(k == addr_pm):
		pm = res[k][2]
	elif(k == addr_ps):
		ps = res[k][2]
	elif(k == addr_ps2):
		ps2 = res[k][2]
	elif(k == addr_sa):
		sa = res[k][2]
	elif(k == addr_scp):
		scp = res[k][2]
	print(v[0])
	for i in instruments:
		spt = i.checkSupport(v[0][1])
		if spt:
			print(spt)
			break
