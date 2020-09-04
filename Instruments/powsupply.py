from Instruments.instrument import Channel, Instrument
# from Instruments.validators import strict_discrete_set

class PSChannel(Channel):
	def __init__(self, channel, adapter, parent, **kwargs):
		super(PSChannel, self).__init__(channel, adapter, parent, **kwargs)

class PS(Instrument):
	models = ["PS", "GENH\d\d-\d\d"]
	def __init__(self, name, adapter, enableSCPI=True, **kwargs):
		super(PS, self).__init__(name, adapter, enableSCPI, **kwargs)
		self.write('SYST:ERR:ENABLE')

# 	mode = Instrument.control("SYST:SET %s", "SYST:SET?", "Output state, REM or LOC",
# 							strict_discrete_set, ["REM", "LOC"])
# 	output = Instrument.control("OUTP:STAT %s", "OUTP:STAT?", "Output state, ON or OFF",
# 							strict_discrete_set, ["ON", "OFF"])
# 	voltage = Instrument.control("VOLT %d", "VOLT?", "DC voltage, in Volts")
# 	meas_voltage = Instrument.measurement("MEAS:VOLT?", "DC voltage, in Volts")
# 	current = Instrument.control("CURR %d", "CURR?", "DC current, in Amps")
# 	meas_current = Instrument.measurement("MEAS:CURR?", "DC current, in Amps")
	
	def set_frequency_start_stop(self, start, stop):
		self.write(':SENS1:FREQ:STAR ' + str(start))
		self.write(':SENS1:FREQ:STOP ' + str(stop))

	def set_frequency_center_span(self, center, span=None):
		self.write('SENS1:FREQ:CENT ' + str(center))
		if not span == None:
			self.write('SENS1:FREQ:SPAN ' + str(span))

	def cmd_mode(self, mode=None):
		if mode == None:
			return self.ask('SYST:SET?')
		elif mode in self._MODES:
			self.write('SYST:SET ' + mode)
		else:
			print("Mode (" + mode + ") not in " + str(self._MODES))

	def output_mode(self):
		return self.ask('SOUR:MODE?')

	def output_state(self, output=None):
		if output == None:
			return self.ask('OUTP:STAT?')
		elif output in self._ONOFF:
			self.write('OUTP:STAT ' + output)
		else:
			print("Output state (" + output + ") not in " + str(self._ONOFF))

	def overcurrent_state(self, output=None):
		if output == None:
			return self.ask('SOUR:CURR:PROT:STAT?')
		elif output in self._ONOFF:
			self.write('SOUR:CURR:PROT:STAT ' + output)
		else:
			print("Output state (" + output + ") not in " + str(self._ONOFF))

	def current(self, c=None, meas=True):
		if c == None:
			if meas == True:
				return self.ask('MEAS:CURR?')
			else:
				return self.ask('SOUR:CURR?')
		else:
			self.write('SOUR:CURR ' + str(c))

	def voltage(self, v=None, meas=True):
		if v == None:
			if meas == True:
				return self.ask('MEAS:VOLT?')
			else:
				return self.ask('SOUR:VOLT?')
		else:
			self.write('SOUR:VOLT ' + str(v))

	def overcurrent(self, oc=None):
		if oc == None:
			return self.ask('SOUR:CURR:PROT:LEV?')
		else:
			self.write('SOUR:CURR:PROT:LEV ' + str(oc))

	def overvoltage(self, ov=None):
		if ov == None:
			return self.ask('SOUR:VOLT:PROT:LEV?')
		else:
			self.write('SOUR:VOLT:PROT:LEV ' + str(ov))

	def undervoltage(self, uv=None):
		if uv == None:
			return self.ask('SOUR:VOLT:LIM:LOW?')
		else:
			self.write('SOUR:VOLT:LIM:LOW ' + str(uv))

	def tripped(self):
		return self.tripped_OVP() or self.tripped_OCP()

	def tripped_OVP(self):
		return self.ask('SOUR:VOLT:PROT:TRIP?')

	def tripped_OCP(self):
		return self.ask('SOUR:CURR:PROT:TRIP?')
