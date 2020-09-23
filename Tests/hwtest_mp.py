# -*- coding: utf-8 -*-
"""
Created on Thu Aug  8 12:29:52 2019

@author: asasson
"""

import sys
sys.path.append('H:\\Python\\axslib')
sys.path.append('H:\\Python\\l3hlib')
import Console

debugOn = False
debugRF = False
debugRED = False
debugBLK = False
debugTime = False
reset_type = False

t_com = [33,36,37,39,40]
t_red = [27,28]
t_blk = [8,9,16,17,30,89]
t_rf  = [2,3,11]

def initMPtest(self, red, blk, debugOn=True, debugR=True, debugB=True, debugRF=False):
	if debugOn : print("****** Initiating tests ")
	for i in range(3):
		if debugOn : print(i)
		tests = t_com
		if(i==1 and debugRED):
			if debugOn : print("****** Beginning RED Tests ******")
			tests.append(t_red)
			hwtest_red(tests)
		elif(i==2 and debugBLK):
			if debugOn : print("****** Beginning BLK Tests ******")
			tests.append(t_blk)
			hwtest_blk(tests)
		elif(i==3 and debugRF):
			if debugOn : print("****** Beginning RF/IF Tests ******")
		
		for t in tests:
			hwtest(t)
	
def hwtest_blk(self, tests):
	for t in tests:
		hwtest(t)

def hwtest_red(self, tests):
	for t in tests:
		hwtest(t)

def hwtest(self, tnum):
	if debugOn : print("****** Beginning hwtest -t ",str(tnum))

if __name__ == "__main__":
	debugOn = True
	#debugRF = True
	debugRED = True
	debugBLK = True
	debugTime = True
	#reset_type = True
	
	if(debugRED):
		red = Console.Console('COM16')
	
	if(debugBLK):
		blk = Console.Console('COM17')
	
	initMPtest(red, blk, debugOn, debugRED, debugBLK, debugRF)


