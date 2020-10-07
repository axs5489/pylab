# -*- coding: utf-8 -*-
"""
Created on Thu Feb 12 12:29:52 2020

@author: asasson
"""

import sys
sys.path.append('H:\\Python\\l3hlib')
import Radio.radio
import Utilities.devmngr
import time
import msvcrt

class TestAborted(Exception):
	pass
	
class Test():
	def __init__(self, dm=None, filename=None, debugOn=False):
		""" Generic Test Constructor
		dm: DevMNGR object
		filename: log file name ('.txt')"""
		self._debugOn = debugOn
		self._name = "GenericTest"
		if(dm == True) :
			self._dm = Utilities.devmngr.Station(filename, debugOn)
			self._dm.autoinit()
		else:
			self._dm = None
	
	def close(self):
		self._dm = None
		self._name = None
		self._debugOn = None
		self._resources = None
		self._rm = None
		self._visaresources = None
	
	def __del__(self):
		self.close()
	
	def GetRadioName(self, radio):
		""" Gets a "nice" name from a given Radio class. """
		radio_name = 'unassigned'
		if type(radio).__name__ == 'F3MP_Radio':
			radio_name = '117G'
		elif type(radio).__name__ == 'F3HH_Radio':
			radio_name = '152'
		elif type(radio).__name__ == 'MCMP_Radio':
			radio_name = '158'
		elif type(radio).__name__ == 'MCHH_Radio':
			radio_name = '163'
		elif type(radio).__name__ == 'STCMP_Radio':
			radio_name = '167'
		elif type(radio).__name__ == 'RF335_BBFixture':
			radio_name = '163 (fixture)'
		else:
			radio_name = type(radio).__name__
		return radio_name
	
	def CheckForTestAbort(raise_exception=True):
		""" Checks for a 'q' keypress, and raises the TestAborted Exception if so."""
		if msvcrt.kbhit():
			if msvcrt.getch() == 'q':
				if raise_exception:
					raise TestAborted('Aborting...')
				else:
					print('Aborting...')
					return True
		return False