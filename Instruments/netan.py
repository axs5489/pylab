from Instruments.instrument import Instrument, HPIBInstrument
import numpy as np

class NetAnalyzer(Instrument):
	models = ["NA", r"E507\dC"]
	def __init__(self, name, adapter, **kwargs):
		super(NetAnalyzer, self).__init__(name, adapter, **kwargs)

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

	def get_trace(self):
		freqList = [float(i) for i in self.ask(':SENS1:FREQ:DATA?').split(',')]
		amplList = [float(i) for i in self.ask(':CALC1:DATA:FDAT?').split(',')[::2]]
		return np.transpose([freqList, amplList])
		
	def save_trace(self, filename):
		np.savetxt(filename, self.get_trace(), delimiter='\t')
		return 0


class HP4396(HPIBInstrument):
	models = ["NA", r"4396B"]
	_MEAS = {'ref':'S11', 'fwd':'S21', 'bwd':'S12', 'rev':'S22'}
	_TRG = {'free':'TRGS INT;CONT', 'hold':'T1', 'imm':'T2', 'delay':'T3'}
	def __init__(self, name, adapter, **kwargs):
		super(HP4396, self).__init__(name, adapter, **kwargs)
		self._id = 'HP4396B'
		self.premeas = "MEAS "
	
	def averaging(self, avg = None):
		if(avg == None):
			return int(self.query("AVER?".format(self.chnum)))
		elif(avg in self._ONOFF):
			self.write("AVER {}".format(avg))
		else:
			print("INVALID ENABLE for AVERAGE: ", avg)
	
	def format(self, f = "LOGM"):
		if(f == "LOGM"):
			self.write("FMT LOGM")
		else:
			self.write("FMT LIN")
	
	def marker(self, m = True):
		if(m):
			self.write('MKR ON')
		else:
			self.write('MKR OFF')
	
	def search(self, m = "MAX"):
		if(m in self._LEVELS):
			self.write('SEAM {}'.format(m))
			return self.query("OUTPMKR?")
	
	def mode(self, m = "NA"):
		if(m == "NA"):
			self.write('NA')
		else:
			self.write('SA')

	def set_frequency_start_stop(self, start, stop):
		self.write('STAR ' + str(start))
		self.write('STOP ' + str(stop))

	def set_frequency_center_span(self, center, span=None):
		self.write('CENT ' + str(center))
		if(span != None):
			self.write('SPAN ' + str(span))