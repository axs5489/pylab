from Instruments.instrument import Instrument
from Instruments.validators import strict_discrete_set

class Channel(object):
	SOURCE_VALUES = ['CH1', 'CH2', 'CH3', 'CH4', 'MATH']
	COUPLING_VALUES = ['AC', 'DC', 'DCREJ']
	
	def __init__(self, parent, num):
		self.parent = parent
		self.num = num
		self.preamble = "MEAS:IMM" + num
		
	def bandwidth(self, bw = None):
		if(bw == None):
			return self.parent.ask("CH%e:BAN?" % (self.num))
		else:
			return self.parent.ask("CH%e:BAN %e" % (self.num, bw))
		
	def coupling(self, cpl = None):
		if(cpl == None):
			return self.parent.ask("CH%e:COUP?" % (self.num))
		elif(cpl in self.COUPLING_VALUES):
			return self.parent.ask("CH%e:COUP %s" % (self.num, cpl))
		else:
			raise ValueError("Invalid coupling ('%s') provided to %s" % (cpl, self.parent))
		
	def deskew(self, offset = None):
		if(offset == None):
			return self.parent.ask("CH%e:DESK?" % (self.num))
		elif(abs(offset) <= 125e-9 and (offset % 40e-12 == 0)):
			return self.parent.ask("CH%e:DESK %e" % (self.num, offset))
		else:
			raise ValueError("Invalid deskew time ('%s') provided to %s" % (offset, self.parent))
		
	def label(self, name = None):
		if(name == None):
			return self.parent.ask("CH%e:LAB:NAM?" % (self.num))
		else:
			return self.parent.ask("CH%e:LAB:NAM %s" % (self.num, name))
		
	def offset(self, voffset = None):
		if(voffset == None):
			return self.parent.ask("CH%e:OFFS?" % (self.num))
		else:
			return self.parent.ask("CH%e:OFFS %e" % (self.num, voffset))
		
	def position(self, pos = None):
		if(pos == None):
			return self.parent.ask("CH%e:POS?" % (self.num))
		else:
			return self.parent.ask("CH%e:POS %d" % (self.num, pos))
		
	def scale(self, div = None):
		if(div == None):
			return self.parent.ask("CH%e:SCA?" % (self.num))
		else:
			return self.parent.ask("CH%e:SCA %e" % (self.num, div))
		
	def scaleratio(self, div = None):
		if(div == None):
			return self.parent.ask("CH%e:SCALERAT?" % (self.num))
		else:
			return self.parent.ask("CH%e:SCALERAT %d" % (self.num, div))
		
	def termination(self, term = None):
		if(term == None):
			return self.parent.ask("CH%e:TER?" % (self.num))
		elif(term == 50 or term == 1e6):
			return self.parent.ask("CH%e:TER %e" % (self.num, term))
		else:
			raise ValueError("Invalid termination ('%s') provided to %s" % (term, self.parent))
		
	def probe(self):
		# FORMAT: MODEL, SERNUM, GAIN, UNITS, TYPE, 
		return self.parent.ask("CH%e:PRO?" % (self.num))
		
	def gain(self):
		return self.parent.ask("CH%e:PRO:GAIN?" % (self.num))
	
	@property
	def value(self):
		return self.parent.values("%sVAL?" % self.preamble)

	@property
	def source(self):
		return self.parent.ask("%sSOU?" % self.preamble).strip()

	@source.setter
	def source(self, value):
		if value in self.SOURCE_VALUES:
			self.parent.write("%sSOU %s" % (self.preamble, value))
		else:
			raise ValueError("Invalid source ('%s') provided to %s" % (
							 self.parent, value))

	@property
	def type(self):
		return self.parent.ask("%sTYP?" % self.preamble).strip()

	@type.setter
	def type(self, value):
		if value in self.TYPE_VALUES:
			self.parent.write("%sTYP %s" % (self.preamble, value))
		else:
			raise ValueError("Invalid type ('%s') provided to %s" % (
							 self.parent, value))

	@property
	def unit(self):
		return self.parent.ask("%sUNI?" % self.preamble).strip()

	@unit.setter
	def unit(self, value):
		if value in self.UNIT_VALUES:
			self.parent.write("%sUNI %s" % (self.preamble, value))
		else:
			raise ValueError("Invalid unit ('%s') provided to %s" % (
							 self.parent, value))

class Oscilloscope(Instrument):
	models = ["SCP", "[DM]SO\d\d\d\d[ABCD]?"]
	acq_modes = ["AVE", "ENV", "SAM", "PEAK", "HIR"]
	def __init__(self, name, adapter, enableSCPI=True, **kwargs):
		super(Oscilloscope, self).__init__(name, adapter, enableSCPI, **kwargs)
		self._maxsamplerate = self.query("ACQuire:MAXSamplerate?")
		self.ch1 = Channel(self, 1)
		self.ch2 = Channel(self, 2)
		self.ch3 = Channel(self, 3)
		self.ch4 = Channel(self, 4)

	acq_mode = Instrument.control('ACQ:MOD?"','FUNC "%s"', "FUNCTION",
							strict_discrete_set, acq_modes)

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

	def save_image(self, drive, filename, filetype = 'bmp'):
		if(filetype in ['bmp', 'jpg', 'png']):
			self.write('SAVE:IMAGE %s%s.%s' % (drive, filename, filetype))
	
	def save_setup(self, drive, filename, includerefs = 'OFF'):
		self.write('SAVE:SETUP:INCLUDEREF %s' % (includerefs))
		self.write('SAVE:SETUP %s%s.set' % (drive, filename))

