from Instruments.instrument import Instrument
from Instruments.validators import truncated_range
import numpy as np

class SpecAnalyzer(Instrument):
	models = ["SpA", "E440\dB"]
	
	def __init__(self, name, adapter, enableSCPI=True, **kwargs):
		super(SpecAnalyzer, self).__init__(name, adapter, enableSCPI, **kwargs)
	
	start_frequency = Instrument.control(":SENS:FREQ:STAR?;", ":SENS:FREQ:STAR %e Hz;",
		""" A floating point property that represents the start frequency (Hz)."""
	)
	stop_frequency = Instrument.control(":SENS:FREQ:STOP?;", ":SENS:FREQ:STOP %e Hz;",
		""" A floating point property that represents the stop frequency (Hz)."""
	)
	frequency_points = Instrument.control(":SENSe:SWEEp:POINts?;", ":SENSe:SWEEp:POINts %d;",
		""" An integer property that represents the number of frequency	points in the sweep [101,8192].
		""", validator=truncated_range,values=[101, 8192],cast=int
	)
	frequency_step = Instrument.control(":SENS:FREQ:CENT:STEP:INCR?;", ":SENS:FREQ:CENT:STEP:INCR %g Hz;",
		""" A floating point property that represents the frequency step (Hz)."""
	)
	center_frequency = Instrument.control(":SENS:FREQ:CENT?;", ":SENS:FREQ:CENT %e Hz;",
		""" A floating point property that represents the center frequency (Hz)."""
	)
	sweep_time = Instrument.control(":SENS:SWE:TIME?;", ":SENS:SWE:TIME %.2e;",
		""" A floating point property that represents the sweep time (seconds)."""
	)
	
	@property
	def frequencies(self):
		""" Returns a numpy array of frequencies in Hz that 
		correspond to the current settings of the instrument.
		"""
		return np.linspace(self.start_frequency, self.stop_frequency,
			self.frequency_points, dtype=np.float64
		)

	def trace(self, number=1):
		""" Returns a numpy array of the data for a particular trace
		based on the trace number (1, 2, or 3).
		"""
		self.write(":FORMat:TRACe:DATA ASCII;")
		data = np.loadtxt(StringIO(self.ask(":TRACE:DATA? TRACE%d;" % number)),
			delimiter=',',	dtype=np.float64
		)
		return data

	def trace_df(self, number=1):
		""" Returns a pandas DataFrame containing the frequency
		and peak data for a particular trace, based on the 
		trace number (1, 2, or 3).
		"""
		return pd.DataFrame({
			'Frequency (GHz)': self.frequencies*1e-9,
			'Peak (dB)': self.trace(number)
		})
	
	def set_frequency_range(self, start, stop):
		self.write(':SENS1:FREQ:STAR ' + str(start))
		self.write(':SENS1:FREQ:STOP ' + str(stop))

	def set_frequency_center_span(self, center, span=None):
		self.write('SENS1:FREQ:CENT ' + str(center))
		if not span == None:
			self.write('SENS1:FREQ:SPAN ' + str(span))

	def set_sweep_parameters(self, number_of_points, power):
		self.write(':SENS1:SWE:POIN ' + str(number_of_points))
		self.write(':SOUR1:POW ' + str(power))

	def set_averaging(self, enable, number_of_averages=None):
		if enable:
			scpi_parameter = 'ON'
		else:
			scpi_parameter = 'OFF'
		self.write(':SENS:AVER ' + scpi_parameter)
		
		if not number_of_averages == None:
			self.write(':SENS:AVER:COUN ' + str(number_of_averages))

	def restart_averaging(self):
		self.write(':SENS:AVER:CLE')

	def get_sweep_time(self):
		return float(self.ask(':SENS1:SWE:TIME?'))

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

	def save_screen(self, filename):
		urllib.request.urlretrieve('http://' + self.host + '/image.asp', filename)
		urllib.request.urlretrieve('http://' + self.host + '/disp.png', filename)


class SignalAnalyzer(SpecAnalyzer):
	models = ["SA", "N9020A"]
	gpib_address = 'GPIB0::18::INSTR'
	tcpip_address = 'TCPIP0::192.168.1.6::inst0::INSTR'
	verbose = 0
	timeout = 60

	def __init__(self, instr_address = gpib_address, verbose = 0):
		self.verbose = verbose
		if self.verbose != 0:
			print("Request connection to analyzer on address: " + str(instr_address))
		self.rm = ResourceManager()
		self.resource = self.rm.open_resource(instr_address) #("GPIB::" + str(gpib_address))
		print(self.resource.query("*IDN?").rstrip(),'\n')

	def reset(self):
		if self.verbose != 0:
			print("Resetting known state")
		self.resource.write("*RST")

		if self.verbose != 0:
			print("Reset Done")


	def close(self):
		if self.verbose != 0:
			print("Closing instrument")
		self.resource.close()
	def open(self):
		if self.verbose != 0:
			print("Opening instrument")
		self.resource.open()		

	# Low-level commands to access it all (should you wish to experiment)
	def ask(self, text):
		return self.resource.ask(text)
	def ask_for_values(self, *args, **kwargs):
		return self.resource.ask_for_values(*args, **kwargs)
	def read(self):
		return self.resource.read()
	def write(self, text):
		return self.resource.write(text)

	# Some common higher level functionality:
	def set_center_frequency(self, frequencyMHz):
		return self.resource.write(":SENSe:FREQuency:CENTer %f MHz" % frequencyMHz)
	def set_span(self, spanMHz):
		return self.resource.write(":SENSe:FREQuency:SPAN %f MHz" % spanMHz)
	def set_sweep_time(self, timeS):
		return self.resource.write(":SENSe:SWEep:TIME %f" % timeS)

	def set_trace_format_ascii(self):
		return self.resource.write(":FORMat:TRACe:DATA ASCii")
	def set_trace_format_float(self):
		self.resource.write(":FORMat:TRACe:DATA REAL,32")
		return self.resource.write(":FORMat:BORDer SWAP")

	def read_trace(self, traceNum):
		self.resource.write(":TRACe:DATA? TRACE%d" % traceNum)
		return self.resource.read()

	def set_burst_mode(self):
		return self.resource.write(":CONF:TXP")
	def set_frequency(self, freq):
		return self.resource.write(":SENS:FREQ:CENT %d" % freq)
	def set_avg_hold_state(self, state):
		return self.resource.write(":TXP:AVER %s" % state)
	def set_avg_hold_num(self, num):
		return self.resource.write(":TXP:AVER:COUN %d" % num)
	def set_avg_hold_mode(self, mode):
		return self.resource.write(":TXP:AVER:TCON %s" % mode)
	def set_avg_type(self, type):
		return self.resource.write(":TXP:AVER:TYPE %s" % type)
	def set_threshold_type(self, type):
		return self.resource.write(":TXP:THR:TYPE %s" % type)
	def set_threshold_lvl(self, level):
		return self.resource.write(":TXP:THR %e" % level)
	def set_measure_method(self, method):
		return self.resource.write(":TXP:THR:TYPE %s" % method)
	def set_bandwidth(self, bw):
		return self.resource.write(":TXP:BAND %s" % bw)
	def set_bar_graph(self, state):
		return self.resource.write("DISP:TXP:BARG %s" % state)
	def set_bw_res(self, res):
		return self.resource.write("SENS:BAND:RES %s" % res)
	def set_freq_span(self, span):
		return self.resource.write("SENS:FREQ:SPAN %s" % span)
	def set_sweep_time(self, sweep_time):
		return self.resource.write("SWE:TIME %e" % sweep_time)
	def set_trigger_source(self, source):
		return self.resource.write(":TRIG:SOUR %s" % source)
	def set_trigger_lvl(self, level):
		return self.resource.write(":TRIG:VID:LEV: %e" % level)
	def set_trigger_slope(self, slope):
		return self.resource.write(":TRIG:SLOP %s" % slope)
	def set_trigger_delay_state(self, state):
		return self.resource.write(":TRIG:RFB:DEL:STAT %s" % state)
	def set_trigger_delay(self, delay):
		return self.resource.write(":TRIG:DEL %e" % delay)
	def read_power(self):
		self.resource.write(':FETC:TXP?')
		return self.resource.read()