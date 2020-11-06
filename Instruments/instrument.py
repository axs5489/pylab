import re
import numpy as np
import visa

from Adapters.adapter import FakeAdapter
from Adapters.visa import VISAAdapter

def splitResourceID(idn, dlm=',', debugOn = False):
	try:
		if(dlm == ','):
			ci1 = idn.find(dlm)
			if(ci1 == -1):
				dlm = ' '
			else:
				ci2 = idn.find(dlm, ci1 + 1)
				ci3 = idn.find(dlm, ci2 + 1)
				mfg = idn[0:ci1].strip()
				mdl = idn[ci1+1 : ci2].strip()
				sn = idn[ci2+1 : ci3].strip()
		if(dlm == ' '):
			ci1 = idn.find(dlm)
			ci2 = idn.find(dlm, ci1 + 1)
			mfg = ''
			mdl = idn[ci1+1 : ci2].strip()
			sn = idn[ci2+1 : ].strip()
			
	except ValueError:
		print("IDN is in improper format")
		return None
	res = (mfg, mdl, sn)
	if debugOn : print(ci1, mfg)
	if debugOn : print(ci2, mdl)
	if debugOn : print(ci3, sn)
	return res

class BaseInstrument():
	""" Base class for all Instruments, independent of Adapter used to communicate with the instrument.
		:param makemodel: A string name
		:param adapter: An :class:`Adapter<l3hlib.Adapters.adapter>` object
	"""
	models = []
	_LEVELS = ["MIN", "MAX", "DEF"]
	_MODES = ["LOC", "REM", "LLO"]
	_ONOFF = [0, 1, "OFF", "ON"]
	_ACDC = ["AC", "DC"]
	
	def __init__(self, name, adapter, **kwargs):
		try:
			if isinstance(adapter, (int, str)):
				print(adapter)
				try:
					adapter = VISAAdapter(adapter, adapter, **kwargs)
				except visa.VisaIOError as e:
					print("Visa IO Error: check connections")
					print(e)
		except ImportError:
			raise Exception("Invalid Adapter provided for Instrument since PyVISA is not present")
		
		self._name = name
		self._adapter = adapter
		self._active = True
		
	def close(self):
		self._name = None
		if(hasattr(self, "_adapter") and hasattr(self._adapter,"close")):
			self._adapter.close()
		self._adapter = None
		self._active = None

	def __del__(self):
		self.close()

	@classmethod
	def checkSupport(cls, model):
		if(cls.models is []):
			return False
		for m in cls.models:
			result = re.search(m, model)
			if(result):
				#print(result, cls.models[0])
				return cls.models[0]
		return None

	@property
	def id(self):
		""" Requests and returns the identification of the instrument. """
		try:
			return self._adapter.ask("*IDN?").strip()
		except:
			try:
				return self._adapter.ask("ID?").strip()
			except:
				if(hasattr(self, "_id")):
					return self._id
				else:
					return "Warning: Identification error."

	# Wrapper functions for the Adapter object
	def ask(self, command):
		""" Sends command to the instrument and returns the read response. """
		return self._adapter.ask(command).strip()
	query = ask

	def write(self, command):
		""" Sends command to the instrument through its adapter. """
		self._adapter.write(command)

	def read(self):
		""" Returns read response from instrument through its adapter. """
		return self._adapter.read()

	def readBytes(self, size, dec = False):
		""" Returns read response from instrument through its adapter. """
		bs = self._adapter.read_bytes(size)
		if dec:
			try:
				return float(bs)
			except:
				return bs
		else:
			return bs

	def value(self, command, **kwargs):
		""" Reads a value from the instrument through the adapter. """
		return self._adapter.values(command, **kwargs)[0]

	def values(self, command, **kwargs):
		""" Reads a set of values from the instrument through the adapter,
		passing on any key-word arguments.
		"""
		return self._adapter.values(command, **kwargs)

	def binary_values(self, command, header_bytes=0, dtype=np.float32):
		return self._adapter.binary_values(command, header_bytes, dtype)
	
	def configure(self, func):
		""" Configures instrument for function """
		if(func in self.functions):
			self.write('FUNC "{}"'.format(func))

	def clear(self):
		""" Clears the instrument status byte """
		self.write("*CLS")
	
	def command(self, cmd, value=None, validator=None):
		if(value is None):
			print("{}?".format(cmd))
			return self.ask("{}?".format(cmd))
		else:
			print("{} {}".format(cmd, value))
			if(validator is None):
				if(isinstance(value, str)):
					return self.write("{} {}".format(cmd, value))
				elif(value):
					return self.write("{} ON".format(cmd))
				else:
					return self.write("{} OFF".format(cmd))
			elif(value in validator):
				return self.write("{} {}".format(cmd, value))
			else:
				raise ValueError("Invalid {} command {} with value {}".format(self, cmd, value))

	def command_state(self, command, bool):
		state = 'ON' if bool else 'OFF'
		return self.write(command + ' ' +  state)

	def command_value(self, command, value, units=''):
		return self.write(command + ' ' + str(value) + units)

	def reset(self):
		""" Resets the instrument. """
		self.write("*RST")

	def wait(self):
		""" Instructs the instrument to wait. """
		self.write("*WAI")

	@staticmethod
	def control(get_command, set_command, docs,
				validator=lambda v, vs: v, values=(), map_values=False,
				get_process=lambda v: v, set_process=lambda v: v,
				check_set_errors=False, check_get_errors=False,
				**kwargs):
		"""Returns a property for the class based on the supplied
		commands. This property may be set and read from the
		instrument.

		:param get_command: A string command that asks for the value
		:param set_command: A string command that writes the value
		:param docs: A docstring that will be included in the documentation
		:param validator: A function that takes both a value and a group of valid values
						  and returns a valid value, while it otherwise raises an exception
		:param values: A list, tuple, range, or dictionary of valid values, that can be used
					   as to map values if :code:`map_values` is True.
		:param map_values: A boolean flag that determines if the values should be
						  interpreted as a map
		:param get_process: A function that take a value and allows processing
							before value mapping, returning the processed value
		:param set_process: A function that takes a value and allows processing
							before value mapping, returning the processed value
		:param check_set_errors: Toggles checking errors after setting
		:param check_get_errors: Toggles checking errors after getting
		"""

		if map_values and isinstance(values, dict):
			# Prepare the inverse values for performance
			inverse = {v: k for k, v in values.items()}

		def fget(self):
			vals = self.values(get_command, **kwargs)
			if check_get_errors:
				self.check_errors()
			if len(vals) == 1:
				value = get_process(vals[0])
				if not map_values:
					return value
				elif isinstance(values, (list, tuple, range)):
					return values[int(value)]
				elif isinstance(values, dict):
					return inverse[value]
				else:
					raise ValueError(
						'Values of type `{}` are not allowed '
						'for Instrument.control'.format(type(values))
					)
			else:
				vals = get_process(vals)
				return vals

		def fset(self, value):
			value = set_process(validator(value, values))
			if not map_values:
				pass
			elif isinstance(values, (list, tuple, range)):
				value = values.index(value)
			elif isinstance(values, dict):
				value = values[value]
			else:
				raise ValueError(
					'Values of type `{}` are not allowed '
					'for Instrument.control'.format(type(values))
				)
			self.write(set_command.format(value))
			if check_set_errors:
				self.check_errors()

		# Add the specified document string to the getter
		fget.__doc__ = docs

		return property(fget, fset)

	@staticmethod
	def measurement(get_command, docs, values=(), map_values=None,
					get_process=lambda v: v, command_process=lambda c: c,
					check_get_errors=False, **kwargs):
		""" Returns a property for the class based on the supplied
		commands. This is a measurement quantity that may only be
		read from the instrument, not set.

		:param get_command: A string command that asks for the value
		:param docs: A docstring that will be included in the documentation
		:param values: A list, tuple, range, or dictionary of valid values, that can be used
					   as to map values if :code:`map_values` is True.
		:param map_values: A boolean flag that determines if the values should be
						  interpreted as a map
		:param get_process: A function that take a value and allows processing
							before value mapping, returning the processed value
		:param command_process: A function that take a command and allows processing
							before executing the command, for both getting and setting
		:param check_get_errors: Toggles checking errors after getting
		"""

		if map_values and isinstance(values, dict):
			# Prepare the inverse values for performance
			inverse = {v: k for k, v in values.items()}

		def fget(self):
			vals = self.values(command_process(get_command), **kwargs)
			if check_get_errors:
				self.check_errors()
			if len(vals) == 1:
				value = get_process(vals[0])
				if not map_values:
					return value
				elif isinstance(values, (list, tuple, range)):
					return values[int(value)]
				elif isinstance(values, dict):
					return inverse[value]
				else:
					raise ValueError(
						'Values of type `{}` are not allowed '
						'for Instrument.measurement'.format(type(values))
					)
			else:
				return get_process(vals)

		# Add the specified document string to the getter
		fget.__doc__ = docs

		return property(fget)

	@staticmethod
	def setting(set_command, docs,
				validator=lambda x, y: x, values=(), map_values=False,
				set_process=lambda v: v,
				check_set_errors=False,
				**kwargs):
		"""Returns a property for the class based on the supplied
		commands. This property may be set, but raises an exception
		when being read from the instrument.

		:param set_command: A string command that writes the value
		:param docs: A docstring that will be included in the documentation
		:param validator: A function that takes both a value and a group of valid values
						  and returns a valid value, while it otherwise raises an exception
		:param values: A list, tuple, range, or dictionary of valid values, that can be used
					   as to map values if :code:`map_values` is True.
		:param map_values: A boolean flag that determines if the values should be
						  interpreted as a map
		:param set_process: A function that takes a value and allows processing
							before value mapping, returning the processed value
		:param check_set_errors: Toggles checking errors after setting
		"""

		if map_values and isinstance(values, dict):
			# Prepare the inverse values for performance
			inverse = {v: k for k, v in values.items()}

		def fget(self):
			raise LookupError("Instrument.setting properties can not be read.")

		def fset(self, value):
			value = set_process(validator(value, values))
			if not map_values:
				pass
			elif isinstance(values, (list, tuple, range)):
				value = values.index(value)
			elif isinstance(values, dict):
				value = values[value]
			else:
				raise ValueError(
					'Values of type `{}` are not allowed '
					'for Instrument.control'.format(type(values))
				)
			self.write(set_command.format(value))
			if check_set_errors:
				self.check_errors()

		# Add the specified document string to the getter
		fget.__doc__ = docs

		return property(fget, fset)


class HPIBInstrument(BaseInstrument):
	""" Class for old HPIB equipment that don't follow the SCPI standard. """
	_MEAS = {}
	_TRG = {'free':'T0', 'hold':'T1', 'imm':'T2', 'delay':'T3'}

	def __init__(self, name, adapter, **kwargs):
		super(HPIBInstrument,self).__init__(name, adapter, **kwargs)
		self.measurement = None
		self.premeas = ""
		self.reset()
		self.auto()
		self.trigger()
	
	def auto(self):
		self.write('AU')

	def id(self):
		""" Override base class implementation since this instrument does not have the standard '*IDN?' command """
		return self._id
		
	def measure(self,type=None):
		if(type == None):
			return self.measurement
		else:
			cmdString = self._MEAS[type.lower()]
			self.measurement = type
			self.write(self.premeas + cmdString)
	
	def reset(self):
		self.write('CL')
		
	def trigger(self, mode='free'):
		""" Method to trigger """
		self.write(self._TRG[mode])


class Instrument(BaseInstrument):
	""" Intermediate class for equipment, implementing common SCPI commands. """

	def __init__(self, name, adapter, **kwargs):
		super(Instrument,self).__init__(str(name), adapter, **kwargs)
		if(isinstance(name, str)):
			name = splitResourceID(name)
		if(isinstance(name, tuple)):
			self._mfg = name[0]
			self._mdl = name[1]
			self._sn = name[2]
		# Basic SCPI commands
		self.status = self.measurement("*STB?", """ Returns the status of the instrument """)
		self.complete = self.measurement("*OPC?", """ TODO: Add this doc """)
		#print(self.display())
		#print(self.selftest())
		#print(self.version())
		#print(self.status())
		#self.beep()
		#self.recover(True)

	def interact(self, tad = 31, lad = 31):
		""" Instructs the instrument to talk to/listen from a certain address. 31 is is the Unlisten/Untalk address """
		self.write("TAD {}".format(tad))
		self.write("LAD {}".format(lad))

	def beep(self):
		""" Clears the instrument status byte """
		self.write("SYST:BEEP")

	def complete(self):
		return self.ask('*OPC?')
	
	def fetch(self):
		return self.value("FETC?")

	def readValue(self):
		""" Returns measurement value at next trigger """
		return self.value("READ?")

	def measure(self):
		""" Returns measurement value """
		return self.value("MEAS?")

	def trigger(self):
		"""Trigger a measurement"""
		self.write("*TRG")

	def error(self):
		"""Return any accumulated errors."""
		return self.ask("SYST:ERR?")

	def check_error(self):
		"""Prints any accumulated errors and returns True if there are."""
		e = self.error()
		print(e)
		if(e.find("+0") >= 0):
			return False
		else:
			return True

	def recover(self, reset=False):
		"""Return any accumulated errors."""
		while(self.check_error()):
			self.clear()
		if(reset) : self.reset()

	def recall(self, state=None):
		"""Recall a saved state."""
		self.write("*RCL " + str(state))

	def save(self, state=None):
		"""Saves a state."""
		self.write("*SAV " + str(state))

	def selftest(self):
		"""Trigger self-test"""
		return self.ask("*TST?")

	def shutdown(self):
		"""Brings the instrument to a safe and stable state"""
		self.isShutdown = True
		print("Shutting down %s".format(self._name))

	def status(self):
		return self.ask("*STAT")

	def display(self):
		"""Return display setting"""
		return self.ask("SYST:DISP?")

	def version(self):
		"""Return SCPI version"""
		return self.ask("SYST:VERS?")

	def wait(self):
		return self.write("*WAI")


class Channel(BaseInstrument):
	""" Intermediate class for equipment with multiple channels. """

	def __init__(self, channel, adapter, parent, **kwargs):
		super(Channel,self).__init__(str(channel), adapter, **kwargs)
		self.chnum = channel
		self.parent = parent
	
	def close(self):
		self.chnum = None
		self.parent = None
		super(Channel,self).close()
	
	def getChannel(self):
		return self.chnum
	
	def command(self, cmd, value=None, validator=None):
		if(hasattr(self,'preamble')):
			msg = self.preamble + cmd
			if(value is None):
				print("{}?".format(msg))
				return self.ask("{}?".format(msg))
			else:
				print("{} {}".format(msg, value))
				if(validator is None):
					if(isinstance(value, str)):
						return self.write("{} {}".format(msg, value))
					elif(value):
						return self.write("{} ON".format(msg))
					else:
						return self.write("{} OFF".format(msg))
				elif(value in validator):
					return self.write("{} {}".format(msg, value))
				else:
					raise ValueError("Invalid {} command {} with value {}".format(self, msg, value))
		else:
			raise ValueError("{} has no preamble".format(self))
	
	def control(self, getcmd, setcmd, docs):
		def fget(self):
			vals = self.values(getcmd.format(self.chnum), **kwargs)
			if len(vals) == 1:
				return vals[0]
			else:
				return vals

		def fset(self, value):
			#value = validator(value, values)
			self.write(setcmd.format(self.chnum, value))

		# Add the specified document string to the getter
		fget.__doc__ = docs
		return property(fget, fset)
	
	def measurement(self, getcmd, docs):
		def fget(self):
			vals = self.values(getcmd.format(self.chnum), **kwargs)
			if len(vals) == 1:
				return vals[0]
			else:
				return vals

		# Add the specified document string to the getter
		fget.__doc__ = docs
		return property(fget)
	
	def setting(self, setcmd, docs):
		def fget(self):
			raise LookupError("Channel.setting properties can not be read.")

		def fset(self, value):
			#value = validator(value, values)
			self.write(setcmd.format(self.chnum, value))

		# Add the specified document string to the getter
		fget.__doc__ = docs
		return property(fget, fset)
	
class ChannelizedInstrument(Instrument):
	""" Class for equipment with channels. """

	def __init__(self, name, adapter, **kwargs):
		super(ChannelizedInstrument,self).__init__(name, adapter, **kwargs)
		self.channels = []
		self.active = 1
	
	def close(self):
		for i in range(len(self.channels)):
			self.remChannel(len(self.channels) - i - 1)
		del self.channels
		del self.active
	
	def addChannel(self, ch):
		if(isinstance(ch, Channel)):
			if(ch.chnum == -1):
				self.channels.append(ch)
				ch.chnum = len(self.channels)
				setattr(self,"ch{}".format(ch.chnum), ch)
			elif(ch.chnum > 0):
				self.channels[ch.chnum - 1] = ch
				setattr(self,"ch{}".format(ch.chnum), ch)
			else:
				print("Invalid index {} for Instrument Channel {}".format(ind, ch))
		else:
			print("Needs to be a Channel Object!")
	
	def getChannel(self, ind):
		return self.channels[ind]
	
	def remChannel(self, ind = -1):
		self.channels[ind].close()
		del self.channels[ind]
		if(ind == -1):
			delattr(self, "ch{}".format(len(self.channels) + 1))
		elif(ind >= 0):
			delattr(self, "ch{}".format(ind + 1))
		else:
			print("Invalid index {} for Instrument Channel {}".format(ind, ch))
		
	
class ConfiguredInstrument(Instrument):
	""" Class for equipment that can save/recall configurations. """

	def __init__(self, name, adapter, **kwargs):
		super(ConfiguredInstrument,self).__init__(name, adapter, **kwargs)

	def addr(self, gpib = 31):
		""" Instructs the instrument to talk to/listen from a certain address. 31 is is the Unlisten/Untalk address """
		self.write("SYST:COMM:GPIB:ADDR {}".format(gpib))
		self.write('*SAV 0')
	
	def recall(self):
		self.write('RCL')
	
	def save(self):
		self.write('SAV')
	
class MathInstrument(Instrument):
	""" Class for equipment with Math capabilities. """

	def __init__(self, name, adapter, **kwargs):
		super(MathInstrument,self).__init__(name, adapter, **kwargs)
	
class Meter(Instrument):
	""" Intermediate class for meter-type equipment. """

	def __init__(self, name, adapter, **kwargs):
		super(Meter,self).__init__(name, adapter, **kwargs)

class RFInstrument(Instrument):
	""" Intermediate class for RF-type equipment. """

	def __init__(self, name, adapter, **kwargs):
		super(RFInstrument,self).__init__(name, adapter, **kwargs)

class RFSweepInstrument(Instrument):
	""" Intermediate class for RF-type equipment that sweep through a frequency range. """

	def __init__(self, name, adapter, **kwargs):
		super(RFSweepInstrument,self).__init__(name, adapter, **kwargs)
