from Instruments.instrument import Instrument
import numpy as np

class Attenuator(Instrument):
	models = ["ATT", r"API8312"]
	
	def __init__(self, makemodel, adapter, **kwargs):
		super(Attenuator, self).__init__(makemodel, adapter, **kwargs)
		self.reset()
	
	def attenuate(self, att = None):
		if(att == None):
			return self.value("ATTN?".format(self.chnum))
		elif(isinstance(att, int) or isinstance(att, float)):
			self.write("ATTN {}".format(att))
		else:
			print("INVALID ATTENUATION: ", att)
	
	def step(self, size = None):
		if(size == None):
			return self.value("STEPSIZE?".format(self.chnum))
		elif(isinstance(size, int) or isinstance(size, float)):
			self.write("STEPSIZE {}".format(size))
		else:
			print("INVALID STEP SIZE: ", size)
		
	def setAttn(self,attenuation):
		""" Method to set the attenuation on the instrument"""
		cmd = 'ATTN %.0f'%(attenuation)
		self.write(cmd)
		
	def setStepSize(self,stepSize):
		""" Method to set the step size """
		cmd = 'STEPSIZE %.3f'%(stepSize)
		self.write(cmd)

	def incr(self):
		""" Method to increment the attenuation by the step size """
		self.write('INCR')

	def decr(self):
		""" Method to decrement the attenuation by the step size """
		self.write('DECR')
  