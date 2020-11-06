from Instruments.instrument import HPIBInstrument
import numpy as np
import urllib.request

class ModulationAnalyzer(HPIBInstrument):
	models = ["MOD", r"8901[AB]"]
	measurement = 'sinad'
	att = {'auto':'1.0', '0db':'1.1', '10db-':'1.2', '20db':'1.3', '30db':'1.4', '40db':'1.5', '50db':'1.6'}
	detTypes = {'peak+':'D1', 'peak-':'D2', 'peak hold':'D3', 'avg':'D4'}
	_MEAS = {'am':'M1', 'fm':'M2', 'pm':'M3', 'power':'M4', 'frequency':'M5', 'audio frequency':'S1', 'audio distortion':'S2' }
	_LPF = {'off':'L0', '3k':'L1', '15k':'L2', '20k':'L3'}
	_HPF = {'off':'H0', '50':'H1', '300':'H2'}
	fmDeEmTimes = {'0us':'P0', '25us':'P2', '50us':'P3', '75us':'P4', '750us':'P5'}
	def __init__(self, name, adapter, **kwargs):
		super(ModulationAnalyzer, self).__init__(name, adapter, **kwargs)
		self.attenuate()
		self._id = 'HP8901A'

	def attenuate(self, att = 'auto'):
		self.write(self.att[att])
	
	def deemphasis(self,time='0us'):
		cmdString = self.fmDeEmTimes[time.lower()]
		self.write(cmdString)
	
	def detector(self,type='peak+'):
		cmdString = self.detTypes[type.lower()]
		self.write(cmdString)

	def filters(self,lowPass='off',highPass='off'):
		cmdString = self._LPF[lowPass.lower()] + self._HPF[highPass.lower()]
		self.write(cmdString)
		
	def setLogLin(self,type='log'):
		if type=='log':
			self.write('LG')
		else:
			self.write('LN')
	
	def getMeasurement(self): 
		""" 
		Method to get the configured measurement result.  Assumes the measurement type has already
		been configured.
			
		Returns: 
			val (float): result read from display
		"""
		val = self._getLevel()
		return val
		
	def ratio(self, mode=False):
		""" Method to enable ratio (dB) """
		self.write("R{}".format(2 if mode else 0))
	
	def _getLevel(self):
		result = self.readBytes(17,'float')

		if result >= 9000000000:
			result -= 9000000000.0
			result /= 100000.0
			if result == 10:
				result = 100
			else:
				result = 0
		return result

class AudioAnalyzer(HPIBInstrument):
	models = ["AA", r"8903[AB]"]
	measurement = 'sinad'
	_MEAS = {'rms':'A0', 'avg':'A1', 'ac level':'M1', 'sinad':'M2', 'distortion':'M3', 'dc level':'S1', 'snr':'S2', 'distortion level':'S3'}
	_LPF = {'off':'L0', '30k':'L1', '80k':'L2'}
	_HPF = {'off':'H0', 'left':'H1', 'right':'H2'}
	_READ = {'left':'RL', 'right':'RR'}
	def __init__(self, name, adapter, **kwargs):
		super(AudioAnalyzer, self).__init__(name, adapter, **kwargs)
		self._id = 'HP8903A'
		
	def amp(self,amplitude=5):
		""" Method to set the amplitude of the Audio Out port
		@amplitude (float) - signal amplitude in mV
		"""
		self.write('AP%.3fMV'%(amplitude))
		
	def filters(self,lowPass='off',highPass='off'):
		cmdString = self._LPF[lowPass] + self._HPF[highPass]
		self.write(cmdString)
	
	def freq(self,val=1000):
		self.write('FR%.3fHZ'%(val))
		
	def getSinad(self,numAverages=1): 
		""" 
		Method to get the Sinad measurement.  Assumes the measurement type has already
		been configured for SINAD
		
		Args:
			numAverages (int): Number of measurements to take
			
		Returns: 
			avg (float): averaged SINAD value
		"""
		values = list()
		for num in range(0,numAverages):
			val = self._getLevel()
			values.append(val)
		
		#check if the data is any good
		stddev = np.std(values)
		if stddev > 1.0:
			#the measurement values were not very precise so the mean is worthless
			#the high STDEV is likely due to settling in analyzer and/or radio, so take last measurment.
			# self.logger.info("SINAD STDEV is too high (%.2f), repeating measurements"%stddev)
			print("SINAD STDEV is high (%.2f), using last measurement instead of mean"%stddev)
			return values[-1]
		else:
			return np.mean(values)
		
	def getAcLevel(self):
		""" Method to get the AC level measurement.  Assumes the measurement type has already
		been configured for AC level
		"""
		return self._getLevel()
	
	def getDistortion(self):
		""" Method to get the Distortion measurement.  Assumes the measurement type has already
		been configured for Distortion
		"""
		return self._getLevel()
		
	def ratio(self, mode=False):
		""" Method to enable ratio """
		self.write("R{}".format(1 if mode else 0))
		
	def step(self, mode='ampl',dir='up'):
		""" Method to step freq (FN) or amplitude (AN) up (SU) or down (SD) by step size """
		if(mode == 'ampl'):
			self.write('AN')
		else:
			self.write('FN')
		
		if(dir == 'up'):
			self.write('UP')
		else:
			self.write('DN')
	
	def _getLevel(self):
		self.write('RR')
		#result, status = self.read(self.Inst.session, 12)
		result = self.readBytes(12,'float')

		if result >= 9000000000:
			result -= 9000000000.0
			result /= 100000.0
			if result == 10:
				result = 100
			else:
				result = 0
		return result
