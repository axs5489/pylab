from Instruments.instrument import Instrument
import numpy as np
import urllib.request

class ModulationAnalyzer(Instrument):
	models = ["AA", r"8901[AB]"]
	def __init__(self, name, adapter, **kwargs):
		super(ModulationAnalyzer, self).__init__(name, adapter, **kwargs)

class AudioAnalyzer(Instrument):
	models = ["AA", r"8903[AB]"]
	measurementType = 'sinad'
	measCmds = {'sinad':'M2', 'ac level':'M1', 'dc level':'S1', 'distortion':'M3', 'snr':'S2'}
	LPFTypes = {'off':'L0', '30k':'L1', '80k':'L2'}
	HPFTypes = {'off':'H0', 'left':'H1', 'right':'H2'}
	def __init__(self, name, adapter, **kwargs):
		super(AudioAnalyzer, self).__init__(name, adapter, **kwargs)

	def id(self):
		""" Override VisaDevice base class implementation since this instrument does not have the standard '*IDN?' command """
		self._id = 'HP8903A'
		return self._id
	
	def reset(self):
		self.write('CL')
		
	def setFilters(self,lowPass='off',highPass='off'):
		cmdString = self.LPFTypes[lowPass] + self.HPFTypes[highPass]
		self.write(cmdString)
		
		
	def setAmp(self,amplitude=5):
		""" Method to set the amplitude of the Audio Out port
		@amplitude (float) - signal amplitude in mV
		"""
		cmd = 'AP%.3fMV'%(amplitude)
		self.write(cmd)
		
	def setMeasType(self,type='SINAD'):
		cmdString = self.measCmds[type.lower()]
		self.measurementType = type
		self.write(cmdString)
	
	def setFreq(self,val=1000):
		cmd = 'FR%.3fHZ'%(val)
		self.write(cmd)
		
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
			self.logger.info("SINAD STDEV is high (%.2f), using last measurement instead of mean"%stddev)
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
	
	def _getLevel(self):
		self.Inst.write('RR')
		#result, status = self.Inst.visalib.read(self.Inst.session, 12)
		result = self.readBytes(12,'float')

		if result >= 9000000000:
			result -= 9000000000.0
			result /= 100000.0
			if result == 10:
				result = 100
			else:
				result = 0
		return result
