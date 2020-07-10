from .adapter import Adapter, FakeAdapter

try:
	from .visa import VISAAdapter
except ImportError:
	print("ERROR! PyVISA library could not be loaded")

try:
	from .serial import SerialAdapter
	#from pymeasure.adapters.prologix import PrologixAdapter
except ImportError:
	print("ERROR! PySerial library could not be loaded")

try:
	from .vxi11 import VXI11Adapter
except ImportError:
	print("ERROR! VXI-11 library could not be loaded")