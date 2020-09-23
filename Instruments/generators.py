from Instruments.instrument import Instrument, RFInstrument
from Instruments.validators import strict_range, strict_discrete_set, truncated_range

class SigGen(RFInstrument):
	models = ["SG", r"8257D", r"E443\d[CD]"]
	def __init__(self, name, adapter, **kwargs):
		super(SigGen, self).__init__(name, adapter, **kwargs)
		self.amplitude_units = 'Vpp'

	def set_frequency_start_stop(self, start, stop):
		self.write(':SENS1:FREQ:STAR ' + str(start))
		self.write(':SENS1:FREQ:STOP ' + str(stop))

	def set_frequency_center_span(self, center, span=None):
		self.write('SENS1:FREQ:CENT ' + str(center))
		if not span == None:
			self.write('SENS1:FREQ:SPAN ' + str(span))

	def set_sweep_parameters(self, number_of_points, power):
		self.write(':SENS1:SWE:POIN ' + str(number_of_points))
		self.write(':SOUR1:POW ' + str(power))
	
	rf_en = Instrument.control(":OUTP:STAT?;", "OUTP:STAT %s;", "RF OUTPUT, ON or OFF",
							strict_discrete_set, ["ON", "OFF"]
	)
	mod_en = Instrument.control(":OUTP:MOD:STAT?;", "OUTP:MOD:STAT %s;", "MOD OUTPUT, ON or OFF",
							strict_discrete_set, ["ON", "OFF"]
	)

	power = Instrument.control(":POW?;", ":POW %g dBm;",
		""" A floating point property that represents the amplitude (dBm)."""
	)
	power_offset = Instrument.control(":POW:LEV:IMM:OFFset?;", ":POW:LEV:IMM:OFFset %g DB;",
		""" A floating point property that represents the amplitude offset (dB). """
	)
	frequency = Instrument.control(":FREQ?;", ":FREQ %e Hz;",
		""" A floating point property that represents the output frequency (Hz)."""
	)
	start_frequency = Instrument.control(":SOUR:FREQ:STAR?", ":SOUR:FREQ:STAR %e Hz",
		""" A floating point property that represents the start frequency (Hz)."""
	)
	center_frequency = Instrument.control(":SOUR:FREQ:CENT?", ":SOUR:FREQ:CENT %e Hz;",
		""" A floating point property that represents the center frequency (Hz)."""
	)
	stop_frequency = Instrument.control(":SOUR:FREQ:STOP?", ":SOUR:FREQ:STOP %e Hz",
		""" A floating point property that represents the stop frequency (Hz)."""
	)
	start_power = Instrument.control(":SOUR:POW:STAR?", ":SOUR:POW:STAR %e dBm",
		""" A floating point property that represents the start power (dBm)."""
	)
	stop_power = Instrument.control(":SOUR:POW:STOP?", ":SOUR:POW:STOP %e dBm",
		""" A floating point property that represents the stop power (dBm)."""
	)
	dwell_time = Instrument.control(":SOUR:SWE:DWEL1?", ":SOUR:SWE:DWEL1 %.3f",
		""" A floating point property that represents the settling time (s)
		at the current frequency or power setting."""
	)
	step_points = Instrument.control(":SOUR:SWE:POIN?", ":SOUR:SWE:POIN %d",
		""" An integer number of points in a step sweep."""
	)

	########################
	# Amplitude modulation #
	########################

	AMPLITUDE_SOURCES = {
		'internal':'INT', 'internal 2':'INT2', 
		'external':'EXT', 'external 2':'EXT2'
	}
	has_amplitude_modulation = Instrument.measurement(":SOUR:AM:STAT?",
		""" Reads a boolean value that is True if the amplitude modulation is enabled. """,
		cast=bool
	)
	amplitude_depth = Instrument.control(":SOUR:AM:DEPT?", ":SOUR:AM:DEPT %g",
		""" A floating point property that controls the amplitude modulation
		in percent, which can take values from 0 to 100 %. """,
		validator=truncated_range,
		values=[0, 100]
	)
	amplitude_source = Instrument.control(":SOUR:AM:SOUR?", ":SOUR:AM:SOUR %s",
		""" A string property that controls the source of the amplitude modulation
		signal, which can take the values: 'internal', 'internal 2', 'external', and
		'external 2'. """,
		validator=strict_discrete_set, values=AMPLITUDE_SOURCES, map_values=True
	)

	####################
	# Pulse modulation #
	####################

	PULSE_SOURCES = {'internal':'INT', 'external':'EXT', 'scalar':'SCAL'}
	PULSE_INPUTS = {
		'square':'SQU', 'free-run':'FRUN',
		'triggered':'TRIG', 'doublet':'DOUB', 'gated':'GATE'
	}
	has_pulse_modulation = Instrument.measurement(":SOUR:PULM:STAT?",
		""" Reads a boolean value that is True if the pulse modulation is enabled. """,
		cast=bool
	)
	pulse_source = Instrument.control(
		":SOUR:PULM:SOUR?", ":SOUR:PULM:SOUR %s",
		""" A string property that controls the source of the pulse modulation
		signal, which can take the values: 'internal', 'external', and
		'scalar'. """,
		validator=strict_discrete_set,
		values=PULSE_SOURCES,
		map_values=True
	)
	pulse_input = Instrument.control(
		":SOUR:PULM:SOUR:INT?", ":SOUR:PULM:SOUR:INT %s",
		""" A string property that controls the internally generated modulation
		input for the pulse modulation, which can take the values: 'square', 'free-run',
		'triggered', 'doublet', and 'gated'.
		""",
		validator=strict_discrete_set,
		values=PULSE_INPUTS,
		map_values=True
	)
	pulse_frequency = Instrument.control(
		":SOUR:PULM:INT:FREQ?", ":SOUR:PULM:INT:FREQ %g",
		""" A floating point property that controls the pulse rate frequency in Hertz,
		which can take values from 0.1 Hz to 10 MHz. """,
		validator=truncated_range,
		values=[0.1, 10e6]
	)

	########################
	# Low-Frequency Output #
	########################

	LOW_FREQUENCY_SOURCES = {
		'internal':'INT', 'internal 2':'INT2', 'function':'FUNC', 'function 2':'FUNC2'
	}

	low_freq_out_amplitude = Instrument.control(
		":SOUR:LFO:AMPL? ", ":SOUR:LFO:AMPL %g VP",
		"""A floating point property that controls the peak voltage (amplitude) of the
		low frequency output in volts, which can take values from 0-3.5V""",
		validator=truncated_range,
		values=[0,3.5]
	)

	low_freq_out_source = Instrument.control(
		":SOUR:LFO:SOUR?", ":SOUR:LFO:SOUR %s",
		"""A string property which controls the source of the low frequency output, which
		can take the values 'internal [2]' for the inernal source, or 'function [2]' for an internal
		function generator which can be configured.""",
		validator=strict_discrete_set,
		values=LOW_FREQUENCY_SOURCES,
		map_values=True
	)

	def enable_low_freq_out(self):
		"""Enables low frequency output"""
		self.write(":SOUR:LFO:STAT ON")

	def disable_low_freq_out(self):
		"""Disables low frequency output"""
		self.write(":SOUR:LFO:STAT OFF")

	def config_low_freq_out(self, source='internal', amplitude=3):
		""" Configures the low-frequency output signal.

		:param source: The source for the low-frequency output signal.
		:param amplitude: Amplitude of the low-frequency output
		"""
		self.enable_low_freq_out()
		self.low_freq_out_source = source
		self.low_freq_out_amplitude = amplitude

	#######################
	# Internal Oscillator #
	#######################

	INTERNAL_SHAPES = {
		'sine':'SINE', 'triangle':'TRI', 'square':'SQU', 'ramp':'RAMP', 
		'noise':'NOIS', 'dual-sine':'DUAL', 'swept-sine':'SWEP'
	}
	internal_frequency = Instrument.control(
		":SOUR:AM:INT:FREQ?", ":SOUR:AM:INT:FREQ %g",
		""" A floating point property that controls the frequency of the internal
		oscillator in Hertz, which can take values from 0.5 Hz to 1 MHz. """,
		validator=truncated_range,
		values=[0.5, 1e6]
	)
	internal_shape = Instrument.control(
		":SOUR:AM:INT:FUNC:SHAP?", ":SOUR:AM:INT:FUNC:SHAP %s",
		""" A string property that controls the shape of the internal oscillations,
		which can take the values: 'sine', 'triangle', 'square', 'ramp', 'noise',
		'dual-sine', and 'swept-sine'. """,
		validator=strict_discrete_set,
		values=INTERNAL_SHAPES,
		map_values=True
	)

	def enable(self):
		""" Enables the output of the signal. """
		self.write(":OUTPUT ON;")

	def disable(self):
		""" Disables the output of the signal. """
		self.write(":OUTPUT OFF;")

	def enable_modulation(self):
		self.write(":OUTPUT:MOD ON;")
		self.write(":lfo:sour int; :lfo:ampl 2.0vp; :lfo:stat on;")

	def disable_modulation(self):
		""" Disables the signal modulation. """
		self.write(":OUTPUT:MOD OFF;")
		self.write(":lfo:stat off;")

	def config_amplitude_modulation(self, frequency=1e3, depth=100.0, shape='sine'):
		""" Configures the amplitude modulation of the output signal.

		:param frequency: A modulation frequency for the internal oscillator
		:param depth: A linear depth precentage
		:param shape: A string that describes the shape for the internal oscillator
		"""
		self.enable_amplitude_modulation()
		self.amplitude_source = 'internal'
		self.internal_frequency = frequency
		self.internal_shape = shape
		self.amplitude_depth = depth

	def enable_amplitude_modulation(self):
		""" Enables amplitude modulation of the output signal. """
		self.write(":SOUR:AM:STAT ON")

	def disable_amplitude_modulation(self):
		""" Disables amplitude modulation of the output signal. """
		self.write(":SOUR:AM:STAT OFF")

	def config_pulse_modulation(self, frequency=1e3, input='square'):
		""" Configures the pulse modulation of the output signal.

		:param frequency: A pulse rate frequency in Hertz
		:param input: A string that describes the internal pulse input
		"""
		self.enable_pulse_modulation()
		self.pulse_source = 'internal'
		self.pulse_input = input
		self.pulse_frequency = frequency

	def enable_pulse_modulation(self):
		""" Enables pulse modulation of the output signal. """
		self.write(":SOUR:PULM:STAT ON")

	def disable_pulse_modulation(self):
		""" Disables pulse modulation of the output signal. """
		self.write(":SOUR:PULM:STAT OFF")

	def config_step_sweep(self):
		""" Configures a step sweep through frequency """
		self.write(":SOUR:FREQ:MODE SWE;"
				   ":SOUR:SWE:GEN STEP;"
				   ":SOUR:SWE:MODE AUTO;")

	def enable_retrace(self):
		self.write(":SOUR:LIST:RETR 1")

	def disable_retrace(self):
		self.write(":SOUR:LIST:RETR 0")

	def single_sweep(self):
		self.write(":SOUR:TSW")

	def start_step_sweep(self):
		""" Starts a step sweep. """
		self.write(":SOUR:SWE:CONT:STAT ON")

	def stop_step_sweep(self):
		""" Stops a step sweep. """
		self.write(":SOUR:SWE:CONT:STAT OFF")

class VectorSigGen(SigGen):
	models = ["AWG", r"HP\dA"]
	def __init__(self, name, adapter, **kwargs):
		super(VectorSigGen, self).__init__(name, adapter, **kwargs)


class ArbGen(SigGen):
	""" Represents the Hewlett Packard 33120A Arbitrary Waveform
	Generator and provides a high-level interface for interacting
	with the instrument."""
	models = ["AWG", r"HP\dA", r"335\d\dA"]
	SHAPES = {'sinusoid':'SIN', 'square':'SQU', 'triangle':'TRI', 
		'ramp':'RAMP', 'noise':'NOIS', 'dc':'DC', 'user':'USER'
	}
	
	def __init__(self, name, adapter, **kwargs):
		super(SigGen, self).__init__(name, adapter, **kwargs)

	shape = Instrument.control("SOUR:FUNC:SHAP?", "SOUR:FUNC:SHAP %s",
		""" A string property that controls the shape of the wave,
		which can take the values: sinusoid, square, triangle, ramp,
		noise, dc, and user. """,
		validator=strict_discrete_set, values = SHAPES, map_values=True
	)
	
	arb_srate = Instrument.control(
		"FUNC:ARB:SRAT?", "FUNC:ARB:SRAT %f",
		""" An floating point property that sets the sample rate of the currently selected 
		arbitrary signal. Valid values are 1 µSa/s to 250 MSa/s. This can be set. """,
		validator=strict_range,	values=[1e-6, 250e6],
	)

	frequency = Instrument.control("SOUR:FREQ?", "SOUR:FREQ %g",
		""" A floating point property that controls the frequency of the
		output in Hz. The allowed range depends on the waveform shape
		and can be queried with :attr:`~.max_frequency` and 
		:attr:`~.min_frequency`. """
	)

	max_frequency = Instrument.measurement("SOUR:FREQ? MAX", 
		""" Reads the maximum :attr:`~.HP33120A.frequency` in Hz for the given shape """
	)

	min_frequency = Instrument.measurement("SOUR:FREQ? MIN", 
		""" Reads the minimum :attr:`~.HP33120A.frequency` in Hz for the given shape """
	)

	amplitude = Instrument.control("SOUR:VOLT?", "SOUR:VOLT %g",
		""" A floating point property that controls the voltage amplitude of the
		output signal. The default units are in  peak-to-peak Volts, but can be
		controlled by :attr:`~.amplitude_units`. The allowed range depends 
		on the waveform shape and can be queried with :attr:`~.max_amplitude`
		and :attr:`~.min_amplitude`. """
	)

	max_amplitude = Instrument.measurement("SOUR:VOLT? MAX", 
		""" Reads the maximum :attr:`~.amplitude` in Volts for the given shape """
	)
	min_amplitude = Instrument.measurement("SOUR:VOLT? MIN", 
		""" Reads the minimum :attr:`~.amplitude` in Volts for the given shape """
	)

	offset = Instrument.control("SOUR:VOLT:OFFS?", "SOUR:VOLT:OFFS %g",
		""" A floating point property that controls the amplitude voltage offset
		in Volts. The allowed range depends on the waveform shape and can be
		queried with :attr:`~.max_offset` and :attr:`~.min_offset`. """
	)

	max_offset = Instrument.measurement("SOUR:VOLT:OFFS? MAX", 
		""" Reads the maximum :attr:`~.offset` in Volts for the given shape """
	)

	min_offset = Instrument.measurement(
		"SOUR:VOLT:OFFS? MIN", 
		""" Reads the minimum :attr:`~.offset` in Volts for the given shape """
	)
	AMPLITUDE_UNITS = {'Vpp':'VPP', 'Vrms':'VRMS', 'dBm':'DBM', 'default':'DEF'}
	amplitude_units = Instrument.control("SOUR:VOLT:UNIT?", "SOUR:VOLT:UNIT %s",
		""" A string property that controls the units of the amplitude,
		which can take the values Vpp, Vrms, dBm, and default.
		""",
		validator=strict_discrete_set,
		values=AMPLITUDE_UNITS,
		map_values=True
	)
