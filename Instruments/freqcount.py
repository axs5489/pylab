from Instruments.instrument import Channel, Instrument, Meter
from Instruments.validators import strict_discrete_set
import numpy as np

class FreqCounterChannel(Channel):
	_ATT = [1, 10]
	_IMP = [50, 1000000, "50", "1E6"]
	def __init__(self, channel, adapter, parent, **kwargs):
		super(FreqCounterChannel, self).__init__(channel, adapter, parent, **kwargs)
	
	def atten(self, att = None):
		if(att == None):
			return self.value("INP{}:ATT?".format(self.chnum))
		elif(isinstance(att, int) or isinstance(att, float)):
			self.write("INP{}:ATT {}".format(self.chnum, att))
		else:
			print("INVALID ATTENUATION: ", att)
	
	def coupling(self, cpl = None):
		if(cpl == None):
			return self.query("INP{}:COUP?".format(self.chnum))
		elif(cpl in self._ACDC):
			self.write("INP{}:COUP {}".format(self.chnum, cpl))
		else:
			print("INVALID COUPLING: ", cpl)
	
	def filter(self, flt = None):
		if(flt == None):
			return self.query("INP{}:FILT?".format(self.chnum))
		elif(flt in self._ONOFF):
			self.write("INP{}:FILT {}".format(self.chnum, flt))
		else:
			print("INVALID 100 kHz FILTER STATE: ", flt)
	
	def imp(self, imp = None):
		if(imp == None):
			return self.value("INP{}:IMP?".format(self.chnum))
		elif(imp in self._IMP):
			self.write("INP{}:IMP {}".format(self.chnum, imp))
		else:
			print("INVALID IMPEDANCE: ", imp)

class FreqCounter(Meter):
	models = ["CNT", r"5313\dA"]
	_FUNC = ["MIN", "MAX", "PTP"] # Single channel measurements w/ no params
	_FUNC1 = ["DCYCLE", "FTIME", "RTIME", "NWIDTH", "PWIDTH", "TOT:TIM"] # Ch 1 measurements w/ param(s)
	_FUNC2 = ["PHASE", "TINT"]		# 2-channel measurements
	_FUNC3 = ["FREQ", "PER"]		# Single channel measurements supporting CH3
	_FUNC_OTHER = ["FREQ", "TOT:CONT"]
	_PCNT = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
	# Voltage can also be specified in place of percent
	#  for x1   [-5.125V, 5.125V]
	#  for x10  [-51.25V, 51.25V]
	
	def __init__(self, makemodel, adapter, **kwargs):
		super(FreqCounter, self).__init__(makemodel, adapter, **kwargs)
		self.ch1 = FreqCounterChannel(1, adapter, self, **kwargs)
		self.ch2 = FreqCounterChannel(2, adapter, self, **kwargs)
		self._func = ''
	
	def dutyCycle(self, param = 50, source = 1):
		if(source == 1):
			if(param in self._PCNT):
				self._func = "DCYCLE"
				return self.value("MEAS:DCYCLE? {},(@{})".format(param, source))
			else:
				return print("INVALID FUNCTION PARAMETER: ", param)
		else:
			print("INVALID SOURCES: ", source)
	
	def fallTime(self, lparam = 10, uparam = 90, source = 1):
		if(source == 1):
			if(lparam in self._PCNT and uparam in self._PCNT):
				self._func = "FTIME"
				msg = "MEAS:FTIME? {},{},(@{})".format(lparam, uparam, source)
				print(msg)
				return self.value(msg)
			else:
				return print("INVALID FUNCTION PARAMETERS: ", lparam, " <- ", uparam)
		else:
			print("INVALID SOURCES: ", source)
	
	def riseTime(self, lparam = 10, uparam = 90, source = 1):
		if(source == 1):
			if(lparam in self._PCNT and uparam in self._PCNT):
				self._func = "RTIME"
				return self.value("MEAS:RTIME? {},{},(@{})".format(lparam, uparam, source))
			else:
				return print("INVALID FUNCTION PARAMETERS: ", lparam, " -> ", uparam)
		else:
			print("INVALID SOURCES: ", source)
	
	def freq(self, param = "30e6,1e0", source = 1):
	# Expected Frequency  (MHz)      Resolution (Hz)
	#   Ch 1, 2 :   0.1 -   225   |   1e-16 to 1e+6
	#   Ch  3   : 100   - 3,000   |    1e-7 to 1e+7
		if(source in [1, 2, 3]):
			self._func = "FREQ"
			if(param == None):
				return self.value("MEAS:FREQ? (@{})".format(source))
			else:
				return self.value("MEAS:FREQ? {},(@{})".format(param, source))
		else:
			print("INVALID SOURCES: ", source)
	
	def freqRATIO(self, param = None, s1 = 1, s2 = 2):
		if((s1 == 1 and s2 in [2, 3]) or (s1 in [2, 3] and s2 == 1)):
			if(param == None):
				return self.value("MEAS:FREQ:RAT? (@{})".format(param, chan))
			elif(param > 0 and param < 100):
				return self.value("MEAS:FREQ:RAT? {},(@{})".format(param, chan))
			else:
				return print("INVALID FUNCTION PARAMETER: ", param)
			self._func = "FREQ:RAT"
		else:
			print("INVALID SOURCES: ", s1, " and ", s2)
	
	def period(self, param = "100e-9", source = 1):
	# Expected Period  (ns)         Resolution (s)
	#   Ch 1, 2 :  4.4  - 10e+9   |  1e-23 to 1e-2
	#   Ch  3   :  0.33 - 10e+9   |  1e-24 to 1e-11
		if(source in [1, 2, 3]):
			self._func = "PER"
			if(param == None):
				return self.value("MEAS:PER? (@{})".format(source))
			else:
				return self.value("MEAS:PER? {},(@{})".format(param, source))
		else:
			print("INVALID SOURCES: ", source)
	
	def phase(self):
		self._func = "PHASE"
		return self.value("MEAS:PHASE?")
	
	def func(self, f = None, param = None, source = 1, source2 = None):
		if(f == None):
			self._func = self.query("CONF?")
			return self._func
		elif(f in self._FUNC3 and source in [1,2,3]):
			if(param == None):
				self.write("MEAS:{} (@{})".format(f, param, source))
			elif(param > 0 and param < 100):
				self.write("MEAS:{} {},(@{})".format(f, param, source))
			elif(param):
				self.write("MEAS:{} {},(@{})".format(f, param, source))
			else:
				return print("INVALID FUNC3 PARAMETER: ", param)
		elif(source in [1,2]):
			if(f in self._FUNC2 and source2 in [1,2]):
				self.write("MEAS:{} (@{},@{})".format(f, source, source2))
			elif(f in self._FUNC1):
				if(param == None):
					self.write("MEAS:{} (@{})".format(f, param, source))
				elif(param > 0 and param < 100):
					self.write("MEAS:{} {},(@{})".format(f, param, source))
				elif(param):
					self.write("MEAS:{} {},(@{})".format(f, param, source))
				else:
					return print("INVALID FUNC1 PARAMETER: ", param)
			elif(f in self._FUNC):
				self.write("MEAS:{} (@{})".format(f, source))
			else:
				return print("INVALID FUNCTION: ", f)
		else:
			return print("INVALID CHANNEL: ", source)
		self._func = f
	
	def max(self, source = 1):
		if(source in [1, 2]):
			self._func = "MAX"
			return self.value("MEAS:MAX? (@{})".format(source))
		else:
			print("INVALID SOURCES: ", source)
	
	def min(self, source = 1):
		if(source in [1, 2]):
			self._func = "MIN"
			return self.value("MEAS:MIN? (@{})".format(source))
		else:
			print("INVALID SOURCES: ", source)
	
	def p2p(self, source = 1):
		if(source in [1, 2]):
			self._func = "PTP"
			return self.value("MEAS:PTP? (@{})".format(source))
		else:
			print("INVALID SOURCES: ", source)
	
	def interval(self, source = 1):
		self._func = "TINT"
		if(source == 1):
			return self.value("MEAS:TINT? (@1),(@2)".format(source))
		elif(source == 2):
			return self.value("MEAS:TINT? (@2),(@1)".format(source))
		else:
			print("INVALID SOURCES: ", source)
	
	def nWidth(self, param = 50, source = 1):
		if(source == 1):
			if(param in self._PCNT):
				self._func = "NWIDTH"
				return self.value("MEAS:NWIDTH? {},(@{})".format(param, source))
			else:
				return print("INVALID FUNCTION PARAMETER: ", param)
		else:
			print("INVALID SOURCES: ", source)
	
	def pWidth(self, param = 50, source = 1):
		if(source == 1):
			if(param in self._PCNT):
				self._func = "PWIDTH"
				return self.value("MEAS:PWIDTH? {},(@{})".format(param, source))
			else:
				return print("INVALID FUNCTION PARAMETER: ", param)
		else:
			print("INVALID SOURCES: ", source)
	
	def totalize(self, gate = True, gateTime = None):
	# gateTime: short [100e-5 to 999e-5], long [10e-3 to 1000] seconds
		if(gate):
			self._func = "TOT:TIM"
			return self.value("MEAS:TOT:TIM? {},(@1)".format(gateTime))
		else:
			self._func = "TOT:CONT"
			return self.value("MEAS:TOT:CONT? (@1)")
	
	def meas(self, f = None, param = None, source = 1, source2 = None):
		if(f == None):
			return self.query("CONF?")
		elif(f in self._FUNC or f in self._FUNC1 or f in self._FUNC2 or f in self._FUNC3):
			if(source in [1,2,3]):
				self.func(f, param, source, source2)
				return self.read()
			else:
				print("INVALID CHANNEL: ", source)
		else:
			print("INVALID FUNCTION: ", f)
	
	def read(self, f = None):
		if(f == None):
			return self.query("READ?")
		elif(f in self._FUNC):
			return self.query("READ:{}?".format(f))
			self._func = f
		else:
			print("INVALID FUNCTION: ", f)
	
	def mode(self, m = None, reset = None):
		if(m == None):
			return self.query("INIT:CONT?")
		elif(m in self._ONOFF):
			if(reset):
				return self.query("INIT:AUTO ON")
			else:
				self.write("INIT:AUTO OFF")
			self.write("INIT:CONT {}".format(m))
		else:
			print("INVALID MODE: ", m)
