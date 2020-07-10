# -*- coding: utf-8 -*-
"""
Created on Tue May 12 17:36:17 2020

@author: asasson
"""

from Adapters.visa import VISAAdapter
from Instruments import specan, dmm, powmeter
from Utilities import devmngr, win
import visa

res = {}
def regInstr(addr, mm, adptr, instr):
	res[addr] = [mm, adptr, instr]

instruments = [dmm.DMM, specan.SpecAnalyzer, powmeter.PowerMeter]
addr_sa = "GPIB0::18::INSTR"
addr_dmm = "GPIB0::7::INSTR"
addr_pm = "GPIB0::13::INSTR"

rm = visa.ResourceManager()
print(rm.list_resources())
print(win.listSerialPorts())

if(addr_sa is not None):
	res_sa = rm.open_resource(addr_sa)
	idsa = res_sa.query('*idn?')[:-1]
	mmsa = devmngr.splitResourceID(idsa)
	adptr_sa = VISAAdapter("SpecAn", res_sa)
	instr_sa =  specan.SpecAnalyzer("SpecAn", adptr_sa)
	regInstr(addr_sa, mmsa, adptr_sa, instr_sa)

if(addr_dmm is not None):
	res_dmm = rm.open_resource(addr_dmm)
	iddmm = res_dmm.query('*idn?')[:-1]
	mmdmm = devmngr.splitResourceID(iddmm)
	adptr_dmm = VISAAdapter("DMM", res_dmm)
	instr_dmm =  dmm.DMM("DMM", adptr_dmm)
	regInstr(addr_dmm, mmdmm, adptr_dmm, instr_dmm)

if(addr_pm is not None):
	res_pm = rm.open_resource(addr_pm)
	idpm = res_pm.query('*idn?')[:-1]
	mmpm = devmngr.splitResourceID(idpm)
	adptr_pm = VISAAdapter("PM", res_pm)
	instr_pm =  powmeter.PowerMeter("PM", adptr_pm)
	regInstr(addr_pm, mmpm, adptr_pm, instr_pm)


for k,v in res.items():
	print(k)
	print(v[0])
	for i in instruments:
		print(i.checkSupport(v[0][1]))



