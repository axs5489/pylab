from Instruments.instrument import Channel, Instrument, ChannelizedInstrument
from Instruments.validators import strict_discrete_set

class PSChannel(Channel):
	def __init__(self, channel, adapter, parent, **kwargs):
		super(PSChannel, self).__init__(channel, adapter, parent, **kwargs)

class PS(Instrument):
	models = ["PS"]
	def __init__(self, name, adapter, **kwargs):
		super(PS, self).__init__(name, adapter, **kwargs)
	
	def close(self):
		pass

class MCPS(PS, ChannelizedInstrument):
	models = ["PS"]
	def __init__(self, name, adapter, **kwargs):
		super(PS, self).__init__(name, adapter, **kwargs)
	
	def close(self):
		pass

class LambdaPS(PS):
	models = ["PS", r"GENH\d\d-\d\d"]
	def __init__(self, name, adapter, **kwargs):
		super(LambdaPS, self).__init__(name, adapter, **kwargs)
		self.write('SYST:ERR:ENABLE')

# 	mode = Instrument.control("SYST:SET?", "SYST:SET %s", "Output state, REM or LOC",
# 							strict_discrete_set, ["REM", "LOC"])
# 	output = Instrument.control("OUTP:STAT?", "OUTP:STAT %s", "Output state, ON or OFF",
# 							strict_discrete_set, ["ON", "OFF"])
# 	voltage = Instrument.control("VOLT?", "VOLT %d", "DC voltage, in Volts")
# 	meas_voltage = Instrument.measurement("MEAS:VOLT?", "DC voltage, in Volts")
# 	current = Instrument.control("CURR?", "CURR %d", "DC current, in Amps")
# 	meas_current = Instrument.measurement("MEAS:CURR?", "DC current, in Amps")

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
			self.write('OUTP:STAT ' + str(output))
		else:
			print("Output state (" + output + ") not in " + str(self._ONOFF))
	
	out_en = Instrument.control(":OUTP:STAT?;", "OUTP:STAT %s;", "OUTPUT, ON or OFF",
							strict_discrete_set, [0, 1, "ON", "OFF"]
	)

	def overcurrent_state(self, output=None):
		if output == None:
			return self.ask('SOUR:CURR:PROT:STAT?')
		elif output in self._ONOFF:
			self.write('SOUR:CURR:PROT:STAT ' + output)
		else:
			print("Output state (" + output + ") not in " + str(self._ONOFF))

	curr = Instrument.control("MEAS:CURR?", "SOUR:CURR {}", "Current, Amps")
	def current(self, c=None, meas=True):
		if c == None:
			if meas == True:
				return self.ask('MEAS:CURR?')
			else:
				return self.ask('SOUR:CURR?')
		else:
			self.write('SOUR:CURR ' + str(c))

	volt = Instrument.control("MEAS:VOLT?", "SOUR:VOLT {}", "Voltage, Volts")
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
		
class XantrexPS(PS):
	models = ["PS", r"HPD\d\d-\d\d"]
	def __init__(self, name, adapter, **kwargs):
		nm = ["Xantrex", name[1], name[2]]
		super(XantrexPS, self).__init__(nm, adapter, **kwargs)

	def clear(self):
		""" Resets the instrument to power on state. """
		self.write("CLR")

	curr = Instrument.control("ISET?", "ISET {}", "Current, Amps")
	def current(self, c=None):
		if c == None:
			return self.ask('ISET?')
		else:
			self.write('ISET ' + str(c))

	def meascurrent(self):
		return self.ask('IOUT?')

	def maxcurrent(self, c=None):
		if c == None:
			return self.ask('IMAX?')
		else:
			self.write('IMAX ' + str(c))

	def delay(self, t=None):
		if t == None:
			return self.ask('DLY?')
		else:
			self.write('DLY ' + str(t))

	def fold(self, m=None):
		if m == None:
			return self.ask('FOLD?')
		else:
			self.write('FOLD ' + str(m))

	def hold(self, m=None):
		if m == None:
			return self.ask('HOLD?')
		elif m in self._ONOFF:
			self.write('HOLD ' + str(m))
		else:
			print("Hold state (" + m + ") not in " + str(self._ONOFF))

	def output_state(self, output=None):
		if output == None:
			return self.ask('OUT?')
		elif output in self._ONOFF:
			self.write('OUT ' + str(output))
		else:
			print("Output state (" + output + ") not in " + str(self._ONOFF))

	def overvoltage(self, ov=None):
		if ov == None:
			return self.ask('OVSET?')
		else:
			self.write('OVSET ' + str(ov))

	volt = Instrument.control("VSET?", "VSET {}", "Voltage, Volts")
	def voltage(self, v=None):
		if v == None:
			return self.ask('VSET?')
		else:
			self.write('VSET ' + str(v))

	def measvoltage(self):
		return self.ask('VOUT?')
