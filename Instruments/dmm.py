from Instruments.instrument import Instrument, Meter
from Instruments.validators import strict_discrete_set
import numpy as np

class DMM(Meter):
	models = ["DMM", r"884\dA", r"34410A"]
	functions = ["CAP", "CONT", "CURR:AC", "CURR:DC", "DIOD", "FRES", "FREQ", "PER", "RES", "TEMP:FRTD", "TEMP:RTD", "VOLT:AC", "VOLT:DC", "VOLT:DC:RAT"]
	VALID_ARGS = ['DEF', 'MIN', 'MAX']
	VALID_TYPE_ARGS = ['AC','DC','DC:RAT']
	
	def __init__(self, makemodel, adapter, enableSCPI=True, **kwargs):
		super(DMM, self).__init__(makemodel, adapter, enableSCPI, **kwargs)
		self._range = 'DEF'
		self._resolution = 'DEF'

	mode = Instrument.control('FUNC?"','FUNC "%s"', "FUNCTION",
							strict_discrete_set, functions)
	
	cap = Instrument.measurement("MEAS:CAP? DEF,DEF", "Capacitance, in Farads")
	def capacitance(self, trig=True):
		if trig:
			return float(self.query("MEAS:CAP? %s, %s"%(self._range,self._resolution)))
		else:
			return Instrument.configure("CAP")
	
	cont = Instrument.measurement("MEAS:CONT?", "Continuity, in Ohms")
	def continuity(self, trig=True):
		if trig:
			return float(self.query("MEAS:CONT?"))
		else:
			return Instrument.configure("CONT")
	
	diod = Instrument.measurement("MEAS:DIOD?", "Diode voltage, in Volts")
	def diode(self, trig=True):
		if trig:
			return float(self.query("MEAS:DIOD?"))
		else:
			return Instrument.configure("DIOD")
	
	freq = Instrument.measurement("MEAS:FREQ? DEF,DEF", "Frequency, in Hertz")
	per = Instrument.measurement("MEAS:PER? DEF,DEF", "Period, in Seconds")
	def frequency(self, trig=True):
		if trig:
			return float(self.query("MEAS:FREQ? %s, %s"%(self._range,self._resolution)))
		else:
			return Instrument.configure("FREQ")
	def period(self, trig=True):
		if trig:
			return float(self.query("MEAS:PER? %s, %s"%(self._range,self._resolution)))
		else:
			return Instrument.configure("PER")

	curr_ac = Instrument.measurement("MEAS:CURR:AC? DEF,DEF", "AC current, in Amps")
	curr_dc = Instrument.measurement("MEAS:CURR:DC? DEF,DEF", "DC current, in Amps")
	def current(self, trig=True,type='DC'):
		if type in self.VALID_TYPE_ARGS:
			if trig:
				return float(self.query("MEAS:CURR:%s? %s, %s"%(type.upper(),self._range,self._resolution)))
			else:
				return Instrument.configure("CURR:%s"%(type.upper()))
	
	volt_ac = Instrument.measurement("MEAS:VOLT:AC? DEF,DEF", "AC voltage, in Volts")
	volt_dc = Instrument.measurement("MEAS:VOLT:DC? DEF,DEF", "DC voltage, in Volts")
	voltage_ratio = Instrument.measurement("MEAS:VOLT:DC:RAT? DEF,DEF", "DC voltage, in Volts")
	def voltage(self, trig=True,type='DC'):
		if type in self.VALID_TYPE_ARGS:
			if trig:
				return float(self.query("MEAS:VOLT:%s? %s, %s"%(type.upper(),self._range,self._resolution)))
			else:
				return Instrument.configure("VOLT:%s"%(type.upper()))
	
	res = Instrument.measurement("MEAS:RES? DEF,DEF", "Resistance, in Ohms")
	res_4w = Instrument.measurement("MEAS:FRES? DEF,DEF", "Four-wires (remote sensing) resistance, in Ohms")
	def resistance(self, trig=True,fourwire=False):
		if trig:
			if fourwire:
				return float(self.query("MEAS:TEMP:FRTD? %s, %s"%(self._range,self._resolution)))
			else:
				return float(self.query("MEAS:TEMP:RTD? %s, %s"%(self._range,self._resolution)))
		else:
			if fourwire:
				return Instrument.configure("TEMP:FRES")
			else:
				return Instrument.configure("TEMP:RES")
	
	temp = Instrument.measurement("MEAS:TEMP:RTD?", "Temperature, in ")
	temp_4w = Instrument.measurement("MEAS:TEMP:FRTD?", "Four-wire Temperature, in ")
	def temperature(self, trig=True,fourwire=False):
		if trig:
			if fourwire:
				return float(self.query("MEAS:TEMP:FRTD? %s, %s"%(self._range,self._resolution)))
			else:
				return float(self.query("MEAS:TEMP:RTD? %s, %s"%(self._range,self._resolution)))
		else:
			if fourwire:
				return Instrument.configure("TEMP:FRTD")
			else:
				return Instrument.configure("TEMP:RTD")

	def getTerminal(self): return Instrument.measurement("ROUT:TERM?", "Determine Front/Rear Terminals")
		
	def resolution(self,res='DEF'):
		if res.upper() in self.VALID_ARGS:
			self._resolution = res
		else:
			try:
				self._resolution = float(res)
			except:
				raise Exception('resolution argument is type (%s) must be float type or valid keyword (%s)'%(type(range),self.VALID_ARGS))
		
	def range(self,range='DEF'):
		if range.upper() in self.VALID_ARGS:
			self._range = range
		else:
			try:
				self._range = float(range)
			except:
				raise Exception('range argument is type (%s) must be float type or valid keyword (%s)'%(type(range),self.VALID_ARGS))


	def set_averaging(self, enable, number_of_averages=None):
		scpi_parameter = 'ON' if enable else 'OFF'
		self.write(':SENS:AVER ' + scpi_parameter)

		if not number_of_averages == None:
			self.write(':SENS:AVER:COUN ' + str(number_of_averages))

	def restart_averaging(self):
		self.write(':SENS:AVER:CLE')

	def get_sweep_time(self):
		return float(self.ask(':SENS1:SWE:TIME?'))

	def get_bandwidth_measure(self, dB_down=None):
		self.write(':CALC1:MARK1:BWID ON')
		if not dB_down == None:
			self.write(':CALC1:MARK1:BWID:THR ' + str(dB_down))
		return [float(i) for i in (self.ask(':CALC1:MARK:BWID:DATA?').split(','))]

	def peak_search(self):
		''' Enable peak search, find peak, and return X and Y positions'''
		self.write(':CALC:MARK1:FUNC:TYPE PEAK')
		self.write(':CALC:MARK1:FUNC:EXEC')
		return float(self.ask(':CALC:MARK1:X?')), float(self.ask(':CALC:MARK1:Y?').split(',')[0])

	def max_search(self, marker=None):
		''' Enable max search, find max, and return X and Y positions'''
		if marker == None:
			marker = 1

		marker_text = 'MARK' + str(marker)

		self.write(':CALC:' + marker_text + ' ON')
		self.write(':CALC:' + marker_text + ':FUNC:TYPE MAX')
		self.write(':CALC:' + marker_text + ':FUNC:EXEC')

		return (float(self.ask(':CALC:' + marker_text + ':X?')),
				float(self.ask(':CALC:' + marker_text + ':Y?').split(',')[0]))

	def min_search(self, marker=None):
		'''Enable min search, find min, and return X and Y positions'''
		if marker == None:
			marker = 1

		marker_text = 'MARK' + str(marker)

		self.write(':CALC:' + marker_text + ' ON')
		self.write(':CALC:' + marker_text + ':FUNC:TYPE MIN')
		self.write(':CALC:' + marker_text + ':FUNC:EXEC')

		return (float(self.ask(':CALC:' + marker_text + ':X?')),
				float(self.ask(':CALC:' + marker_text + ':Y?').split(',')[0]))


	def get_trace(self):
		freqList = [float(i) for i in self.ask(':SENS1:FREQ:DATA?').split(',')]
		amplList = [float(i) for i in self.ask(':CALC1:DATA:FDAT?').split(',')[::2]]
		return np.transpose([freqList, amplList])

	def set_marker(self, freq, marker=None):
		if marker == None:
			marker = 1

		marker_text = 'MARK' + str(marker)

		self.write(':CALC:' + marker_text + ':X ' + str(freq))
		return float(self.ask(':CALC:' + marker_text + ':Y?').split(',')[0])

	def get_marker_value(self, marker=None):
		if marker == None:
			marker = 1

		marker_text = 'MARK' + str(marker)

		return float(self.ask(':CALC:' + marker_text + ':Y?').split(',')[0])

	def save_trace(self, filename):
		np.savetxt(filename, self.get_trace(), delimiter='\t')
		return 0
