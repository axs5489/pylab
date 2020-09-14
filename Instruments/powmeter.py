from Instruments.instrument import Channel, Instrument, RFInstrument
from Instruments.validators import strict_range, strict_discrete_set
import time

class PMChannel(Channel):
	_UNITS = ["w", "W", "dbm", "DBM"]	# LINEAR (W, %) , LOG (dBm, dB)
	_SENSE = ["SENS1", "SENS2", "SENS1-SENS2", "SENS2-SENS1", "SENS1/SENS2", "SENS2/SENS1"]
	def __init__(self, channel, adapter, parent, **kwargs):
		super(PMChannel, self).__init__(channel, adapter, parent, **kwargs)
	
	def init(self):
		return self.query("INIT{}".format(self.chnum))
	
	def measure(self):
		return self.query("MEAS{}?".format(self.chnum))
	
	def power(self):
		return self.query("FETC{}?".format(self.chnum))
			
	def powerStable(self, delay = 0.1, timeout = 10, maxtol = 0.05):
		stable = 0
		maxattempts = 200
		lastpwr = float(self.query("FETC?"))
		lasttime = time.perf_counter()
		for i in range(maxattempts):
			time.sleep(delay)
			pwr = float(self.query("FETC?"))
			dev = abs(pwr - lastpwr)/pwr
			if(dev < maxtol) :
				stable += 1
			else: stable = 0
			if(stable == 5) : return pwr
			if(i == maxattempts) : print("Attempts reached")
			if(time.perf_counter() - lasttime > timeout): return "Time-out"
			lastpwr = pwr
		return None
	
	def read(self):
		return self.query("READ{}?".format(self.chnum))
	
	def offset(self, offset = None):
	#   MIN      DEF       MAX        UNITS
	#  -100 << (  0  ) << +100    W / % / dBm / dB
		if(offset == None):
			return self.query("CALC{}:GAIN?".format(self.chnum))
		elif(isinstance(offset, int) or isinstance(offset, float)):
			self.write("CALC{}:GAIN {}".format(self.chnum, offset))
		else:
			print("INVALID OFFSET: ", offset)
	
	def offsetenable(self, offset = None):
		if(offset == None):
			return self.query("CALC{}:GAIN:STATE?".format(self.chnum))
		elif(offset in self._ONOFF):
			self.write("CALC{}:GAIN:STATE {}".format(self.chnum, offset))
		else:
			print("INVALID OFFSET: ", offset)
	
	def units(self, unit = None):
		if(unit == None):
			return self.query("UNIT{}:POW?".format(self.chnum))
		elif(unit in self._UNITS):
			self.write("UNIT{}:POW {}".format(self.chnum, unit))
		else:
			print("INVALID UNITS: ", unit)
	
	# TTL OUTPUT LIMITS / FAILURES
	def MATH(self, sens = None):
		if(sens == None):
			return self.query("UNIT{}:MATH?".format(self.chnum))
		elif(self.parent._mdl in self.parent.SCmodels):
			return self.write("CALC{}:MATH SENS1".format(self.chnum))
		elif(sens in self._SENSE):
			return self.write("CALC{}:MATH {}".format(self.chnum, sens))
		else:
			print("INVALID MATHS: ", sens)
	
	def clearFailure(self):
		return self.query("CALC{}:LIM:CLE:IMM".format(self.chnum))
	
	def hasFailure(self):
		return self.query("CALC{}:LIM:FAIL?".format(self.chnum))
	
	def numFailure(self, reset = False):
		num = self.query("CALC{}:LIM:FCO?".format(self.chnum))
		if reset : self.clearFailure()
		return num
	
	def enableLIM(self, enlim = None):
		if(enlim == None):
			return self.query("CALC{}:LIM:STAT?".format(self.chnum))
		elif(enlim in self._ONOFF):
			self.write("CALC{}:LIM:STAT {}".format(self.chnum, enlim))
		else:
			print("INVALID LIMITS (ON/OFF): ", enlim)
	
	def lowerLIM(self, lim = None):
	#   MIN      DEF       MAX        UNITS
	#  -150 << ( -90 ) << +200    W / % / dBm / dB
		if(lim == None):
			return self.query("CALC{}:LIM:LOW?".format(self.chnum))
		elif(isinstance(lim, int) or isinstance(lim, float)):
			self.write("CALC{}:LIM:LOW {}".format(self.chnum, lim))
		else:
			print("INVALID LIMITS: ", lim)
	
	def upperLIM(self, lim = None):
	#   MIN      DEF       MAX        UNITS
	#  -150 << ( -90 ) << +200    W / % / dBm / dB
		if(lim == None):
			return self.query("CALC{}:LIM:UPP?".format(self.chnum))
		elif(isinstance(lim, int) or isinstance(lim, float)):
			self.write("CALC{}:LIM:UPP {}".format(self.chnum, lim))
		else:
			print("INVALID LIMITS: ", lim)
		
class PowerMeter(RFInstrument):
	models = ["PM", "E441[89]B"]
	SCmodels = ["E4418B"]
	MCmodels = ["E4419B"]
	_MATH = ["A", "B", "A-B", "B-A", "A/B", "B/A"]
	def __init__(self, name, adapter, **kwargs):
		super(PowerMeter, self).__init__(name, adapter, **kwargs)
		self._num_channels = 1
		self.ch1 = PMChannel(1, adapter, self)
		try:
			if(self._mdl in self.MCmodels):
				print("Dual Channel Power Meter Detected!")
				self._num_channels = 2
				self.ch2 = PMChannel(2, adapter, self)
				readDIF = Instrument.measurement("READ:DIF?", "Power difference, in dB or W")
				readRAT = Instrument.measurement("READ:DIF?", "Power ratio, in dB")
		except:
			print("PowerMeter Exception: 2nd channel initialization")
	
	def close(self):
		self.ch1.close()
		self.ch1 = None
		if(self._num_channels == 2):
			self.ch2.close()
			self.ch2 = None
			readDIF = None
			readRAT = None
		super(PowerMeter,self).close()
	
	refosc = Instrument.control("OUTP:ROSC?", "OUTP:ROSC %s", "Power reference, ON or OFF",
							strict_discrete_set, ["ON", "OFF"]
							)
