# -*- coding: utf-8 -*-
"""
Created on Tue May 12 17:36:17 2020

@author: asasson
"""

from Adapters.visa import VISAAdapter
from Instruments import scope, netan, powmeter
from Utilities import devmngr, win
import visa

res = {}
def regInstr(addr, mm, adptr, instr):
	res[addr] = [mm, adptr, instr]

instruments = [scope.Oscilloscope, netan.NetAnalyzer, powmeter.PowerMeter]
addr_scp = "USB0::0x0699::0x0401::C001731::INSTR"
addr_na = "GPIB0::17::INSTR"
addr_pm = "GPIB0::15::INSTR"

rm = visa.ResourceManager()
print(rm.list_resources())
print(win.listSerialPorts())

if(addr_scp is not None):
	res_scp = rm.open_resource(addr_scp)
	idscp = res_scp.query('*idn?')[:-1]
	mmscp = devmngr.splitResourceID(idscp)
	adptr_scp = VISAAdapter("SpecAn", res_scp)
	instr_scp = scope.Oscilloscope("Oscillocope", adptr_scp)
	regInstr(addr_scp, mmscp, adptr_scp, instr_scp)

if(addr_na is not None):
	res_na = rm.open_resource(addr_na)
	idna = res_na.query('*idn?')[:-1]
	mmna = devmngr.splitResourceID(idna)
	adptr_na = VISAAdapter("NA", res_na)
	instr_na = netan.NetAnalyzer("NA", adptr_na)
	regInstr(addr_na, mmna, adptr_na, instr_na)

if(addr_pm is not None):
	res_pm = rm.open_resource(addr_pm)
	idpm = res_pm.query('*idn?')[:-1]
	mmpm = devmngr.splitResourceID(idpm)
	adptr_pm = VISAAdapter("PM", res_pm)
	instr_pm = powmeter.PowerMeter("PM", adptr_pm)
	regInstr(addr_pm, mmpm, adptr_pm, instr_pm)


for k,v in res.items():
	print(k)
	print(v[0])
	for i in instruments:
		print(i.checkSupport(v[0][1]))



