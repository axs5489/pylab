import re
import numpy as np
import visa

from Adapters.adapter import FakeAdapter
from Adapters.visa import VISAAdapter

class BaseInstrument():
	""" Base class for all Instruments, independent of Adapter used to communicate with the instrument.
		:param makemodel: A string name
		:param adapter: An :class:`Adapter<l3hlib.Adapters.adapter>` object
	"""
	models = []
	_LEVELS = ["MIN", "MAX"]
	_MODES = ["LOC", "REM", "LLO"]
	_ONOFF = ["OFF", "ON"]
	
	def __init__(self, makemodel, adapter, **kwargs):
		try:
			if isinstance(adapter, (int, str)):
				print(adapter)
				try:
					rm = visa.ResourceManager()
					resource = rm.open_resource(adapter)
					adapter = VISAAdapter(adapter, resource, **kwargs)
				except visa.VisaIOError as e:
					print(resource, ":", "Visa IO Error: check connections")
					print(e)
				
		except ImportError:
			raise Exception("Invalid Adapter provided for Instrument since PyVISA is not present")

		self._name = makemodel
		self._adapter = adapter
		if(type(makemodel) is list):
			self._mfg = makemodel[0]
			self._mdl = makemodel[1]
			self._sn = makemodel[2]
		
		self._active = True
		
	def close(self):
		self._name = None
		self._adapter = None
		if(type(self._name) is list):
			self._mfg = None
			self._mdl = None
			self._sn = None

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
		return self._adapter.ask(command)
	query = ask

	def write(self, command):
		""" Sends command to the instrument through its adapter. """
		self._adapter.write(command)

	def read(self):
		""" Returns read response from instrument through its adapter. """
		return self._adapter.read()

	def readValue(self):
		""" Returns measurement value at next trigger """
		return self.ask("READ?")

	def measure(self):
		""" Returns measurement value """
		return self.ask("MEAS?")

	def trigger(self):
		"""Trigger a measurement"""
		self.write("*TRG")

	def values(self, command, **kwargs):
		""" Reads a set of values from the instrument through the adapter,
		passing on any key-word arguments.
		"""
		return self._adapter.values(command, **kwargs)

	def binary_values(self, command, header_bytes=0, dtype=np.float32):
		return self._adapter.binary_values(command, header_bytes, dtype)

	def beep(self):
		""" Clears the instrument status byte """
		self.write("SYST:BEEP")
	
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

	def shutdown(self):
		"""Brings the instrument to a safe and stable state"""
		self.isShutdown = True
		print("Shutting down %s" % self._name)

	def selftest(self):
		"""Trigger self-test"""
		return self.ask("*TST?")

	def status(self):
		"""Trigger self-test"""
		return self.ask("*STAT")

	def display(self):
		"""Return display setting"""
		return self.ask("SYST:DISP?")

	def version(self):
		"""Return SCPI version"""
		return self.ask("SYST:VERS?")

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


	def configure_display_scale(self, reference_value, reference_position=None,
								number_of_divisions=None, scale_per_division=None):
		self.write('DISP:WIND1:TRAC1:Y:RLEV ' + str(reference_value))

		if not reference_position == None:
			self.write('DISP:WIND1:TRAC1:Y:RPOS ' + str(reference_position))

		if not number_of_divisions == None:
			self.write('DISP:WIND1:Y:DIV ' + str(number_of_divisions))

		if not scale_per_division == None:
			self.write('DISP:WIND1:TRAC1:Y:PDIV ' + str(scale_per_division))

	def set_background_color(self, red, green, blue):
		''' Colors are integers of range 0 through 5'''
		self.write('DISP:COL:BACK ' + str(red) + ',' + str(green) + ',' + str(blue))

	def set_graticule_color(self, red, green, blue):
		''' Colors are integers of range 0 through 5'''
		self.write('DISP:COL:GRAT ' + str(red) + ',' + str(green) + ',' + str(blue))

	def set_grid_color(self, red, green, blue):
		''' Colors are integers of range 0 through 5'''
		self.write('DISP:COL:GRAT2 ' + str(red) + ',' + str(green) + ',' + str(blue))

	def get_bandwidth_measure(self, dB_down=None):
		self.write(':CALC1:MARK1:BWID ON')
		if not dB_down == None:
			self.write(':CALC1:MARK1:BWID:THR ' + str(dB_down))
		return [float(i) for i in (self.ask(':CALC1:MARK:BWID:DATA?').split(','))]

	def max_search(self, marker=1):
		''' Enable max search, find max, and return X and Y positions'''
		marker_text = 'MARK' + str(marker)

		self.write(':CALC:' + marker_text + ' ON')
		self.write(':CALC:' + marker_text + ':FUNC:TYPE MAX')
		self.write(':CALC:' + marker_text + ':FUNC:EXEC')

		return (float(self.ask(':CALC:' + marker_text + ':X?')),
				float(self.ask(':CALC:' + marker_text + ':Y?').split(',')[0]))

	def min_search(self, marker=1):
		'''Enable min search, find min, and return X and Y positions'''
		marker_text = 'MARK' + str(marker)

		self.write(':CALC:' + marker_text + ' ON')
		self.write(':CALC:' + marker_text + ':FUNC:TYPE MIN')
		self.write(':CALC:' + marker_text + ':FUNC:EXEC')

		return (float(self.ask(':CALC:' + marker_text + ':X?')),
				float(self.ask(':CALC:' + marker_text + ':Y?').split(',')[0]))

	def peak_search(self):
		''' Enable peak search, find peak, and return X and Y positions'''
		self.write(':CALC:MARK1:FUNC:TYPE PEAK')
		self.write(':CALC:MARK1:FUNC:EXEC')
		return float(self.ask(':CALC:MARK1:X?')), float(self.ask(':CALC:MARK1:Y?').split(',')[0])


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


class Channel(BaseInstrument):
	""" Intermediate class for equipment with multiple channels. """

	def __init__(self, channel, adapter, parent, **kwargs):
		super(Channel,self).__init__(str(channel), adapter, True, **kwargs)
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

	def __init__(self, channel, parent, adapter, enableSCPI=False, **kwargs):
		super(Instrument,self).__init__(str(channel), adapter, **kwargs)
		if enableSCPI:
			# Basic SCPI commands
			self.status = self.measurement("*STB?", """ Returns the status of the instrument """)
			self.complete = self.measurement("*OPC?", """ TODO: Add this doc """)
		#print(self.display())
		#print(self.selftest())
		#print(self.version())
		#print(self.status())
		#self.beep()
		#self.recover(True)

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

class FakeInstrument(Instrument):
	""" Fake implementation for testing purposes. """

	def __init__(self, name=None, adapter=None, enableSCPI=False, **kwargs):
		super().__init__(name or "Fake Instrument", FakeAdapter(), enableSCPI=enableSCPI, **kwargs)

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

	
class Meter(Instrument):
	""" Intermediate class for meter-type equipment. """

	def __init__(self, name, adapter, enableSCPI=False, **kwargs):
		super(Meter,self).__init__(name, adapter, enableSCPI, **kwargs)

class RFInstrument(Instrument):
	""" Intermediate class for RF-type equipment. """

	def __init__(self, name, adapter, enableSCPI=False, **kwargs):
		super(RFInstrument,self).__init__(name, adapter, enableSCPI, **kwargs)

class RFSweepInstrument(Instrument):
	""" Intermediate class for RF-type equipment that sweep through a frequency range. """

	def __init__(self, name, adapter, enableSCPI=False, **kwargs):
		super(RFSweepInstrument,self).__init__(name, adapter, enableSCPI, **kwargs)
