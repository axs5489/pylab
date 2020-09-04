from Instruments.instrument import Instrument, RFInstrument
from Instruments.validators import strict_range, strict_discrete_set, truncated_range

class GSG(Instrument):
	models = ["GPS", r"GSG-\d\d"]
	SIGNAL_MODE_LETTER = ["U", "M", "P"]		# Unmodulated / Modulated / PRN signal
	GNSS_LETTER = {'G' : "GPS",
					'R': "GLONASS",
					'E': "GALILEO",
					'C': "BEIDOU",
					'J': "QZSS",
					'I': "IRNSS",
					'S': "SBAS"}
	SIGNAL_TYPE = ['GPSL1CA','GPSL1P','GPSL1PY','GPSL2P','GPS L2PY',	# GPS
				'GLOL1', 'GLOL2',										# GLONASS
				'GALE1', 'GALE5a', 'GALE5b',							# GALILEO
				'BDSB1', 'BDSB2',										# BeiDou
				'QZSSL1CA', 'QZSSL1SAIF', 'QZSSL2C', 'QZSSL5',			# QZSS
				'IRNSSL5' 												# IRNSS
				]
	ENVIRONMENTS = ['URBAN','SUBURBAN','RURAL','OPEN']
	
	def __init__(self, name, adapter, enableSCPI=True, **kwargs):
		super(GSG, self).__init__(name, adapter, enableSCPI, **kwargs)
	
	status = Instrument.control(":SOUR:ONECHN:CONT?;", "SOUR:ONECHN:CONT %s%s%d;", "Sig Gen execution, START / STOP / ARM",
							strict_discrete_set, ["START", "STOP", "ARM"]
	)
	sat_id = Instrument.control(":SOUR:ONECHN:SAT?;", "SOUR:ONECHN:SAT %s;", "Satelite ID",
	)
	signal = Instrument.control(":SOUR:ONECHN:SIGNAL?;", "SOUR:ONECHN:SIGNAL %s;", "Signal Type",
							strict_discrete_set, SIGNAL_TYPE)
	start = Instrument.control(":SOUR:ONECHN:START?;", "SOUR:ONECHN:START %s;", "Start Time, DD/MM/YYYY hh:mm")
	ephemeris = Instrument.control(":SOUR:ONECHN:EPH?;", "SOUR:ONECHN:EPH %s;", "Ephemeris, filename")
	
	atten = Instrument.control(":OUTP:EXTATT?;", "OUTP:EXTATT %g;", "Attenuation, in dB")
	ext_ref = Instrument.control(":SOUR:EXTREF?;", "SOUR:EXTREF %s;", "External Reference Clock, ON or OFF",
							strict_discrete_set, ["ON", "OFF"]
	)
	noise_en = Instrument.control(":SOUR:NOISE:CONT?;", "SOUR:NOISE:CONT %s;", "Noise simulation, ON or OFF",
							strict_discrete_set, ["ON", "OFF"]
	)
	noise_density = Instrument.control(":SOUR:NOISE:CNO?;", "SOUR:NOISE:CNO %g", "Carrier/Noise density, [0.0, 56.0]",
							strict_range, [0, 56]
	)


	freq_offset = Instrument.control(":SOUR:ONECHN:FREQ?;", ":SOUR:ONECHN:FREQ %s;",
		""" A floating point property that represents the output frequency (Hz).""")
	freq_offset_range = Instrument.control(":SOUR:ONECHN:FREQ?;", ":SOUR:ONECHN:FREQ %d;",
		""" A floating point property that represents the output frequency (Hz).""",
							strict_range, [-6e6, 6e6])
	power = Instrument.control("SOUR:POW?;", "SOUR:POW %g;",
		""" A floating point property that represents the amplitude (dBm).""")
	refpower = Instrument.control("SOUR:REFPOW?;", "SOUR:REFPOW %g;",
		""" A floating point property that represents the reference power (dBm).""")
	pps = Instrument.control(":SOUR:PPSOUT?;", "SOUR:PPSOUT %d;", "PPS OUTPUT, ON or OFF",
							strict_discrete_set, [1, 10, 100, 1000])
	
	prop_env = Instrument.control(":SOUR:SCEN:PROP?;", "SOUR::SCEN:PROP %s;", "Propagation environment",
							strict_discrete_set, ENVIRONMENTS)
	
class GSG_55(GSG):
	models = ["GPS", r"GSG-55"]
	def __init__(self, name, adapter, enableSCPI=True, **kwargs):
		super(GSG, self).__init__(name, adapter, enableSCPI, **kwargs)
		self.amplitude_units = 'Vpp'
	
	noise_bw = Instrument.control(":SOUR:NOISE:BW?;", "SOUR:NOISE:BW %g", "[GSG-55 ONLY] Noise bandwith, [0.001, 20.46]",
							strict_range, [0.001, 20.46]
	)
	noise_offset = Instrument.control(":SOUR:NOISE:OFFSET?;", "SOUR:NOISE:OFFSET %g", "[GSG-55 ONLY] Noise frequency offset, [-10.23, 10.23]",
							strict_range, [-10.23, 10.23]
	)