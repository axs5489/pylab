import re
import numpy as np
import visa

from Adapters.adapter import FakeAdapter
from Adapters.visa import VISAAdapter

def splitResourceID(idn, debugOn = False):
	try:
		ci1 = idn.index(',')
		ci2 = idn.index(',', ci1 + 1)
		ci3 = idn.index(',', ci2 + 1)
		mfg = idn[0:ci1].strip()
		mdl = idn[ci1+1 : ci2].strip()
		sn = idn[ci2+1 : ci3].strip()
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
		self._adapter = None

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

	def reset(self):
		""" Resets the instrument. """
		self.write("*RST")

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
			self.write(set_command % value)
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
			self.write(set_command % value)
			if check_set_errors:
				self.check_errors()

		# Add the specified document string to the getter
		fget.__doc__ = docs

		return property(fget, fset)


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

class Instrument(BaseInstrument):
	""" Intermediate class for equipment with multiple channels. """

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

	def beep(self):
		""" Clears the instrument status byte """
		self.write("SYST:BEEP")
	
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
		print("Shutting down %s" % self._name)

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
		

class FakeInstrument(Instrument):
	""" Fake implementation for testing purposes. """

	def __init__(self, name=None, adapter=None, **kwargs):
		super().__init__(name or "Fake Instrument", FakeAdapter(), **kwargs)

	@staticmethod
	def control(get_command, set_command, docs, validator=lambda v, vs: v, values=(), map_values=False,
				get_process=lambda v: v, set_process=lambda v: v, check_set_errors=False, check_get_errors=False,
				**kwargs):
		"""Fake Instrument.control.

		Strip commands and only store and return values indicated by
		format strings to mimic many simple commands.
		This is analogous how the tests in test_instrument are handled.
		"""

		# Regex search to find first format specifier in the command
		fmt_spec_pattern = r'(%[\w.#-+ *]*[diouxXeEfFgGcrsa%])'
		match = re.search(fmt_spec_pattern, set_command)
		if match:
			format_specifier = match.group(0)
		else:
			format_specifier = ''
		# To preserve as much functionality as possible, call the real
		# control method with modified get_command and set_command.
		return Instrument.control(get_command="", set_command=format_specifier,
								  docs=docs, validator=validator,
								  values=values, map_values=map_values,
								  get_process=get_process, set_process=set_process,
								  check_set_errors=check_set_errors,
								  check_get_errors=check_get_errors, **kwargs)

	
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
