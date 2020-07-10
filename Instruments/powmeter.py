from Instruments.instrument import Instrument, RFInstrument
from Instruments.validators import strict_range, strict_discrete_set
import time

class PowerMeter(RFInstrument):
	models = ["PM", "E4418B"]
	def __init__(self, name, adapter, enableSCPI=True, **kwargs):
		super(PowerMeter, self).__init__(name, adapter, enableSCPI, **kwargs)
		self._num_channels = 1
		try:
			self.dev
		except:
			pass
	
	offset = Instrument.control("CALC:GAIN?", "CALC:GAIN %d", "Offset, in dB or W",
							strict_range, [-100, 100]
							)
	
	offset_enable = Instrument.control("CALC:GAIN:STATE?", "CALC:GAIN:STATE %s", "Offset, ON or OFF",
							strict_discrete_set, ["ON", "OFF"]
							)
	
	units = Instrument.control("UNIT:POW?", "UNIT:POW %s", "Units, in dB or W",
							strict_discrete_set, ["W", "DBM"]
							)
	
	power = Instrument.measurement("FETC?", "Power, in dB or W")
	def fetchPower(self, debugOn = False):
		if debugOn : print("*** FETCH ****")
		pwr = float(self.query("FETC?"))
		if debugOn : print("POWER: ", pwr)
		return pwr

	def fetchStablePower(self, delay = 0.1, timeout = 10, maxtol = 0.05):
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
	


class DualPowerMeter(PowerMeter):
	models = ["PM", "E4419B"]
	def __init__(self, name, adapter, enableSCPI=True, **kwargs):
		super(DualPowerMeter, self).__init__(name, adapter, enableSCPI, **kwargs)
		self._num_channels = 2
		
	power_1 = Instrument.measurement("FETC?", "Power, in dB or W")
	power_2 = Instrument.measurement("FETC?", "Power, in dB or W")
	power_ratio = Instrument.measurement("FETC?", "Power, in dB or W")
	power_rel = Instrument.measurement("FETC?", "Power, in dB or W")
	
	units_2 = Instrument.control("UNIT2:POW?", "UNIT2:POW %s", "Units, in dB or W",
							  strict_discrete_set, ["W", "DBM"]
							  )
	
	units_ratio = Instrument.control("UNIT:POW:RAT?", "UNIT:POW:RAT %s", "Units, in dB or W",
							  strict_discrete_set, ["PCT", "DBM"]
							  )