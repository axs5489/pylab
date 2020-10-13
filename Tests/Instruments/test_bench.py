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
from Instruments.netan import NetAnalyzer
from Instruments.powmeter import PowerMeter#, DualPowerMeter
from Instruments.powsupply import PS
from Instruments.rfswitch import rfSW
from Instruments.scope import Oscilloscope
from Instruments.specan import SpecAnalyzer
from Radio.radio import Console, Channel, Radio
from Utilities import devmngr, win
import visa

res = {}
def regInstr(addr, mm, adptr, instr):
	res[addr] = [mm, adptr, instr]

instruments = [AudioAnalyzer, ArbGen, DMM, FireBERD, FreqCounter, ModulationAnalyzer, 
			NetAnalyzer, PowerMeter, PS, rfSW, SigGen, GSG, SpecAnalyzer, Oscilloscope]
addr_aud = "GPIB0::28::INSTR"
addr_modan = "GPIB0::14::INSTR"
addr_na = "GPIB0::17::INSTR"
addr_pm = "GPIB0::15::INSTR"
addr_scp = "USB0::0x0699::0x0401::C001731::INSTR"
addr_list = [addr_aud,
			addr_modan,
			addr_na,
			addr_pm,
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
			if(addr is addr_aud):
				pass
				adptr = VISAAdapter("TestAdapter", r)
				instr =  AudioAnalyzer("AudioAn", adptr)
				res[addr] = ["AudioAn", adptr, instr]
			if(addr is addr_modan):
				adptr = VISAAdapter("TestAdapter", r)
				instr =  ModulationAnalyzer("ModAn", adptr)
				res[addr] = ["ModAn", adptr, instr]
			else:
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
	if(k == addr_aud):
		aud = res[k][2]
	elif(k == addr_modan):
		modan = res[k][2]
	elif(k == addr_na):
		na = res[k][2]
	elif(k == addr_pm):
		pm = res[k][2]
	elif(k == addr_scp):
		scp = res[k][2]
	print(v[0])
	for i in instruments:
		print(i.checkSupport(v[0][1]))
