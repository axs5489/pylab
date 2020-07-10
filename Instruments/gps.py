from Instruments.instrument import Instrument, RFInstrument
from Instruments.validators import strict_range, strict_discrete_set, truncated_range

class GSG(Instrument):
	models = ["GPS", r"GSG-\d\d"]
	def __init__(self, name, adapter, enableSCPI=True, **kwargs):
		super(GSG, self).__init__(name, adapter, enableSCPI, **kwargs)
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
	
	atten = Instrument.control(":OUTP:EXTATT?;", "OUTP:EXTATT %g;", "Attenuation, in dB")
	ext_ref = Instrument.control(":SOUR:EXTREF?;", "SOUR:EXTREF %s;", "External Reference Clock, ON or OFF",
							strict_discrete_set, ["ON", "OFF"]
	)

	power = Instrument.control("SOUR:POW?;", "SOUR:POW %g;",
		""" A floating point property that represents the amplitude (dBm)."""
	)
	refpower = Instrument.control("SOUR:REFPOW?;", "SOUR:REFPOW %g;",
		""" A floating point property that represents the reference power (dBm)."""
	)
	
	
	pps = Instrument.control(":SOUR:PPSOUT?;", "SOUR:PPSOUT %d;", "PPS OUTPUT, ON or OFF",
							strict_discrete_set, [1, 10, 100, 1000]
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