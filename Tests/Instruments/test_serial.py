# -*- coding: utf-8 -*-
"""
Created on Tue May 12 17:36:17 2020

@author: asasson
"""
import site
site.addsitedir(r'H:\Python\l3hlib')
site.addsitedir(r'C:\Users\asasson\Documents\Python')

from Adapters.visa import VISAAdapter
from Instruments.instrument import splitResourceID
from Instruments.powsupply import PS
from Utilities import win
from Utilities.SerialPort import SerialPort
import time
import visa

stp = "COM1"
red = "COM4"
blk = "COM5"
reduut = "COM6"
blkuut = "COM7"
rcp = "COM53"
com_list = [#stp,
			#red,
			#blk,
			reduut,
			blkuut,
			#rcp
			]
testclass = SerialPort

res = {}
addr_ps = "GPIB0::6::INSTR"
rm = visa.ResourceManager()
try:
	r = rm.open_resource(addr_ps)
	mm = splitResourceID(r.query('*idn?')[:-1])
	print(mm)
	adptr = VISAAdapter("TestAdapter", r)
	ps =  PS(mm, adptr)
	ps.output_state(0)
	ps.voltage(26)
	time.sleep(1)
	ps.output_state(1)
except:
	print("Power Supply Error")
print(rm.list_resources())
print(win.listSerialPorts())

for addr in com_list:
	#print(addr)
	try:
		if(addr is stp):
			stp = testclass('stp',addr)
			if stp.isOpen():
				res[addr] = stp
				#print(res[addr])
		if(addr is red):
			red = testclass('red',addr)
			if red.isOpen():
				res[addr] = red
				#print(res[addr])
		if(addr is blk):
			blk = testclass('blk',addr)
			if blk.isOpen():
				res[addr] = blk
				#print(res[addr])
		if(addr is reduut):
			reduut = testclass('reduut',addr)
			if reduut.isOpen():
				res[addr] = reduut
				#print(res[addr])
		if(addr is blkuut):
			blkuut = testclass('blkuut',addr)
			if blkuut.isOpen():
				res[addr] = blkuut
				#print(res[addr])
		if(addr is rcp):
			rcp = testclass('rcp',addr)
			if rcp.isOpen():
				res[addr] = rcp
				#print(res[addr])
	except:
		print("COM Error: ", addr)

