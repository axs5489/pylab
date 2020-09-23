# -*- coding: utf-8 -*-
"""
Created on Thu Aug  8 12:29:52 2019

@author: asasson
"""

import sys
sys.path.append('H:\\Python\\l3hlib')
import console

debugOn = False
debugTime = False
debugRF = False
debugBLK = True
debugRED = True
debugRCP = True
reset_type = False
tests = []

def initHWtest(self, rcp, red, blk, debugOn=True):
	if debugOn : print("****** Initiating tests ")
	for t in tests:
		if debugOn : print(t)
		if (t==1):
			hwtest(t)
		else:
			hwtest(rcp, t)

def hwtest(self, con, test):
	if debugOn : print("****** Beginning hwtest -t ",str(test))
	con.sendCommand

if __name__ == "__main__":
	debugOn = True
	#
	debugTime = True
	#reset_type = True
	
	try:
		rcp = console.Console('RCP','COM11')
	except:
		print("RCP COM Failed")
	try:
		red = console.Console('RED','COM6')
	except:
		print("RED COM Failed")
	try:
		blk = console.Console('BLK','COM7')
	except:
		print("BLK COM Failed")
	initHWtest(rcp, red, blk, debugOn)
	
	rcp.close()
	red.close()
	blk.close()
	