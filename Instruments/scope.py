from Instruments.instrument import Channel, BaseInstrument, ChannelizedInstrument
from Instruments.validators import strict_discrete_set

class ScopeChannel(Channel):
	_SOURCE_VALUES = ["CH1", "CH2", "CH3", "CH4", "MATH"]
	
	def __init__(self, channel, adapter, parent, **kwargs):
		super(ScopeChannel, self).__init__(channel, adapter, parent, **kwargs)
		
	def coupling(self, cpl = None):
		return self.command(":COUP", cpl, self._CPL)
		
	def offset(self, off = None):
		if(isinstance(off, str) and off.find("+") == -1) : off = int(off)
		if(isinstance(off, int) or isinstance(off, float)) : off = "{:e}".format(off)
		return self.command(":OFFS", off)
		
	def scale(self, div = None):
		if(isinstance(div, str) and div.find("+") == -1) : div = int(div)
		if(isinstance(div, int) or isinstance(div, float)) : div = "{:e}".format(div)
		return self.command(":SCALE", div)

class DSOChannel(ScopeChannel):
	_CPL = BaseInstrument._ACDC
	_IMP = ["ONEM", "FIFT"]
	
	def __init__(self, channel, adapter, parent, **kwargs):
		super(DSOChannel, self).__init__(channel, adapter, parent, **kwargs)
		self.preamble = "CHAN" + str(channel)
	
	def attenuation(self, att = None):
		if(isinstance(att, str) and att.find("+") == -1) : att = int(att)
		if(isinstance(att, int) or isinstance(att, float)) : att = "{:e}".format(att)
		return self.command(":PROB", att)
	
	def bandwidth(self, en = None):
		return self.command(":BWL", en)
	
	def deskew(self, sk = None):
		if(isinstance(sk, str) and sk.find("+") == -1) : sk = int(sk)
		if(isinstance(sk, int) or isinstance(sk, float)) : sk = "{:e}".format(sk)
		return self.command(":PROB:SKEW", sk)
	
	def display(self, en = None):
		return self.command(":DISP", en)
	
	def impedance(self, imp = None):
		return self.command(":IMP", imp, self._IMP)
	
	def invert(self, en = None):
		return self.command(":INV", en)
	
	def label(self, lbl = None):
		if(lbl != None):
			lbl = ("\"" + str(lbl) + "\"").upper()
		return self.command(":LAB", lbl)
	
	def range(self, fs = None):
		if(isinstance(fs, str) and fs.find("+") == -1) : fs = int(fs)
		if(isinstance(fs, int) or isinstance(fs, float)) : fs = "{:e}".format(fs)
		return self.command(":RANG", fs)
	
	def termination(self, hiz = True):
		if(hiz):
			return self.impedance("ONEM")
		else:
			return self.impedance("FIFT")
	
	def vernier(self, en = None):
		return self.command(":VERN", en)

class MSOChannel(ScopeChannel):
	_SOURCE_VALUES = ["CH1", "CH2", "CH3", "CH4", "MATH"]
	_CPL = ["AC", "DC", "DCREJ"]
	
	def __init__(self, channel, adapter, parent, **kwargs):
		super(MSOChannel, self).__init__(channel, adapter, parent, **kwargs)
		self.preamble = "CH" + str(channel)
		self.pre = "MEAS:IMM" + str(channel)
		
	def bandwidth(self, bw = None):
		if(bw == None):
			return self.ask("CH{}:BAN?".format(self.chnum))
		else:
			return self.ask("CH{}:BAN {}".format(self.chnum, bw))
		
	# def coupling(self, cpl = None):
		# if(cpl == None):
			# return self.ask("CH{}:COUP?".format(self.chnum))
		# elif(cpl in self._COUPLING_VALUES):
			# return self.write("CH{}:COUP {}".format(self.chnum, cpl))
		# else:
			# raise ValueError("Invalid coupling {} provided to {}".format(cpl, self.parent))
		
	def deskew(self, offset = None):
		if(offset == None):
			return self.ask("CH{}:DESK?".format(self.chnum))
		elif(abs(offset) <= 125e-9 and (offset.format40e-12 == 0)):
			return self.write("CH{}:DESK {:e}".format(self.chnum, offset))
		else:
			raise ValueError("Invalid deskew time {} provided to {}".format(offset, self.parent))
		
	def label(self, name = None):
		if(name == None):
			return self.ask("CH{}:LAB:NAM?".format(self.chnum))
		else:
			return self.write("CH{}:LAB:NAM {}".format(self.chnum, name))
		
	# def offset(self, voffset = None):
		# if(voffset == None):
			# return self.ask("CH{}:OFFS?".format(self.chnum))
		# else:
			# return self.write("CH{}:OFFS {:e}".format(self.chnum, voffset))
		
	def position(self, pos = None):
		if(pos == None):
			return self.ask("CH{}:POS?".format(self.chnum))
		else:
			return self.write("CH{}:POS %d".format(self.chnum, pos))
		
	# def scale(self, div = None):
		# if(div == None):
			# return self.ask("CH{}:SCA?".format(self.chnum))
		# else:
			# return self.write("CH{}:SCA {:e}".format(self.chnum, div))
		
	def scaleratio(self, div = None):
		if(div == None):
			return self.ask("CH{}:SCALERAT?".format(self.chnum))
		else:
			return self.write("CH{}:SCALERAT {:e}".format(self.chnum, div))
		
	def termination(self, term = None):
		if(term == None):
			return self.ask("CH{}:TER?".format(self.chnum))
		elif(term == 50 or term == 1e6):
			return self.write("CH{}:TER {:e}".format(self.chnum, term))
		else:
			raise ValueError("Invalid termination {} provided to {}".format(term, self.parent))
		
	def probe(self):
		# FORMAT: MODEL, SERNUM, GAIN, UNITS, TYPE, 
		return self.ask("CH{}:PRO?".format(self.chnum))
		
	def gain(self):
		return self.ask("CH{}:PRO:GAIN?".format(self.chnum))
	
	@property
	def value(self):
		return self.values("{}VAL?".format(self.pre))

	@property
	def source(self):
		return self.ask("{}SOU?".format(self.pre).strip())

	@source.setter
	def source(self, value):
		if value in self.SOURCE_VALUES:
			self.write("{}SOU {}".format(self.pre, value))
		else:
			raise ValueError("Invalid source {} provided to {}".format(
							 self.parent, value))

	@property
	def type(self):
		return self.ask("{}TYP?".format(self.pre).strip())

	@type.setter
	def type(self, value):
		if value in self.TYPE_VALUES:
			self.write("{}TYP {}".format(self.pre, value))
		else:
			raise ValueError("Invalid type {} provided to {}".format(
							 self.parent, value))

	@property
	def unit(self):
		return self.ask("{}UNI?".format(self.preamble).strip())

	@unit.setter
	def unit(self, value):
		if value in self.UNIT_VALUES:
			self.write("{}UNI {}".format(self.preamble, value))
		else:
			raise ValueError("Invalid unit {} provided to {}".format(
							 self.parent, value))

class Oscilloscope(ChannelizedInstrument):
	models = ["SCP", r"[DM]SO\d\d\d\d[ABCD]?"]
	
	def __init__(self, name, adapter, **kwargs):
		super(Oscilloscope, self).__init__(name, adapter, **kwargs)

class DSO(Oscilloscope):
	models = ["SCP", r"DSO\d\d\d\d[ABCD]?"]
	_ACQ = ["AVE", "ENV", "SAM", "PEAK", "HIR"]
	_TIM = ["MAIN", "WIND", "XY", "ROLL"]
	
	def __init__(self, name, adapter, **kwargs):
		super(DSO, self).__init__(name, adapter, **kwargs)
		#self._maxsamplerate = self.ask("ACQuire:MAXSamplerate?")
		self.ch1 = DSOChannel(1, adapter, self)
		self.ch2 = DSOChannel(2, adapter, self)
		self.ch3 = DSOChannel(3, adapter, self)
		self.ch4 = DSOChannel(4, adapter, self)
	
	def clearDisplay(self):
		self.write("DISP:CLEAR")
	
	def displayLines(self, en=None):
		return self.command("DISP:VECTORS", en)
	
	def persistence(self, en=None):
		return self.command("DISP:PERS", en, ["INF", "MIN"])
	
	def scale(self, t=None):
		if(isinstance(t, str) and t.find("+") == -1) : t = int(t)
		if(isinstance(t, int) or isinstance(t, float)) : t = "{:e}".format(t)
		return self.command("TIM:SCALE", t)
	
	def winmode(self, m=None):
		return self.command("TIM:MODE", m, self._TIM)
	
	def windelay(self, t=None):
		if(isinstance(t, str) and t.find("+") == -1) : t = int(t)
		if(isinstance(t, int) or isinstance(t, float)) : t = "{:e}".format(t)
		return self.command("TIM:POS", t)
	
	def winrange(self, t=None):
		if(isinstance(t, str) and t.find("+") == -1) : t = int(t)
		if(isinstance(t, int) or isinstance(t, float)) : t = "{:e}".format(t)
		return self.command("TIM:RANGE", t)
	
	def zoomedwindelay(self, t=None):
		if(isinstance(t, str) and t.find("+") == -1) : t = int(t)
		if(isinstance(t, int) or isinstance(t, float)) : t = "{:e}".format(t)
		return self.command("TIM:WIND:POS", t)
	
	def zoomedwinrange(self, t=None):
		if(isinstance(t, str) and t.find("+") == -1) : t = int(t)
		if(isinstance(t, int) or isinstance(t, float)) : t = "{:e}".format(t)
		return self.command("TIM:WIND:RANGE", t)

class MSO(Oscilloscope):
	models = ["SCP", r"MSO\d\d\d\d[ABCD]?"]
	acq_modes = ["AVE", "ENV", "SAM", "PEAK", "HIR"]
	def __init__(self, name, adapter, **kwargs):
		super(MSO, self).__init__(name, adapter, **kwargs)
		self._maxsamplerate = self.ask("ACQuire:MAXSamplerate?")
		self.ch1 = MSOChannel(1, adapter, self)
		self.ch2 = MSOChannel(2, adapter, self)
		self.ch3 = MSOChannel(3, adapter, self)
		self.ch4 = MSOChannel(4, adapter, self)
	
	def autoscale(self):
		self.write("AUT")

	acq_mode = BaseInstrument.control("ACQ:MOD?",'FUNC "%s"', "FUNCTION",
							strict_discrete_set, acq_modes)

	def set_frequency_start_stop(self, start, stop):
		self.write(":SENS1:FREQ:STAR " + str(start))
		self.write(":SENS1:FREQ:STOP " + str(stop))

	def set_frequency_center_span(self, center, span=None):
		self.write("SENS1:FREQ:CENT " + str(center))
		if not span == None:
			self.write("SENS1:FREQ:SPAN " + str(span))

	def set_sweep_parameters(self, number_of_points, power):
		self.write(":SENS1:SWE:POIN " + str(number_of_points))
		self.write(":SOUR1:POW " + str(power))

	def set_averaging(self, enable, number_of_averages=None):
		if enable:
			scpi_parameter = "ON"
		else:
			scpi_parameter = "OFF"
		self.write(":SENS:AVER " + scpi_parameter)

		if not number_of_averages == None:
			self.write(":SENS:AVER:COUN " + str(number_of_averages))

	def restart_averaging(self):
		self.write(":SENS:AVER:CLE")

	def save_image(self, drive, filename, filetype = "bmp"):
		if(filetype in ["bmp", "jpg", "png"]):
			self.write("SAVE:IMAGE {}{}.{}".format(drive, filename, filetype))
	
	def save_setup(self, drive, filename, includerefs = "OFF"):
		self.write("SAVE:SETUP:INCLUDEREF {}".format(includerefs))
		self.write("SAVE:SETUP {}{}.set".format(drive, filename))

	
	def display(self, ch, en=None):
		return self.command("DIG{}:DISP".format(ch), en)
	
	def label(self, lbl = None):
		if(lbl != None):
			lbl = ("\"" + str(lbl) + "\"").upper()
		return self.command("DIG{}:LAB".format(ch), lbl)
	
	def pos(self, p = None):
		return self.command("DIG{}:POS".format(ch), p)
	
	def size(self, sz = None):
		return self.command("DIG{}:SIZE".format(ch), sz, ["SMAL", "MED", "LARG"])
	
	def threshold(self, t = None):
		if(t in ["MCOS", "ECL", "TTL"] or isinstance(t, int) or isinstance(t, float)) :
			return self.command("DIG{}:POS".format(ch), t)
