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
from Radio.radio import Console, Channel, Radio
from Utilities import win
from Utilities.SerialPort import SerialPort
import time
import visa

close = True
com_types = [SerialPort, Console, Channel, Radio]
comcls = com_types[1]
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
			stp = comcls('stp',addr)
			if stp.isOpen():
				res[addr] = stp
				#print(res[addr])
		if(addr is red):
			red = comcls('red',addr)
			if red.isOpen():
				res[addr] = red
				#print(res[addr])
		if(addr is blk):
			blk = comcls('blk',addr)
			if blk.isOpen():
				res[addr] = blk
				#print(res[addr])
		if(addr is reduut):
			reduut = comcls('reduut',addr)
			if reduut.isOpen():
				res[addr] = reduut
				#print(res[addr])
		if(addr is blkuut):
			blkuut = comcls('blkuut',addr)
			if blkuut.isOpen():
				res[addr] = blkuut
				#print(res[addr])
		if(addr is rcp):
			rcp = comcls('rcp',addr)
			if rcp.isOpen():
				res[addr] = rcp
				#print(res[addr])
	except:
		print("COM Error: ", addr)

time.sleep(40)
reduut.flush()
blkuut.flush()
print("LOOPING")
#try:
# while True:
# 	for a,r in res.items():
# 		print(a)
# 		buf = ""
# 		while r.inWaiting() > 0:
# 			#print(r.readline())
# 			buf += r.read(100)
# 			print(buf)
# 			buf = ""
# 			
# 		r.validatePrompt(buf)
# 		if(not r.validatePrompt(buf, True)):
# 			r.send("ASCII")
# 		r.validatePrompt(buf)
# 		time.sleep(1)
# 		print("NEXT")
# 	time.sleep(1)
# 	print("AGAIN")
#except Exception as e:
#	print(e)

if(close):
	for a,r in res.items():
		r.close()