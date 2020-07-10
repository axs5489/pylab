from .adapter import Adapter
#import copy
import visa
import numpy as np

class VISAAdapter(Adapter):
	""" Adapter class for the VISA library using PyVISA to communicate
	with instruments.
	:param resourcename: VISA resource name that identifies the address
	:param resource: VISA resource connection
	:param kwargs: Any valid key-word arguments for constructing a PyVISA instrument
	"""
	def __init__(self, resourceName, resource, **kwargs):
		#if isinstance(resourceName, int):
		#	resourceName = "GPIB0::%d::INSTR" % resourceName
		super(VISAAdapter, self).__init__(resourceName)
		if(isinstance(resource, str)):
			try:
				rm = visa.ResourceManager()
				resource = rm.open_resource(resource)
			except visa.VisaIOError as e:
				print(resource, ":", "Visa IO Error: check connections")
				print(e)
		
		self.connection = resource
		#self.manager = visa.ResourceManager(visa_library)
		#safeKeywords = ['resource_name', 'timeout',	'chunk_size', 'lock', 'delay', 'send_end',
		#				'values_format', 'read_termination', 'write_termination']
		#kwargsCopy = copy.deepcopy(kwargs)
		#for key in kwargsCopy:
		#	if key not in safeKeywords:
		#		kwargs.pop(key)
		#self.connection = self.manager.get_instrument(resourceName, **kwargs)

	def __repr__(self):
		return "<VISAAdapter(resource='%s')>" % self.connection.resourceName

	def ask(self, command):
		""" Writes the command to the instrument and returns the resulting
		ASCII response

		:param command: SCPI command string to be sent to the instrument
		:returns: String ASCII response of the instrument
		"""
		return self.connection.query(command)

	def ask_values(self, command):
		""" Writes a command to the instrument and returns a list of formatted
		values from the result. The format of the return is configurated by
		self.config().

		:param command: SCPI command to be sent to the instrument
		:returns: Formatted response of the instrument.
		"""
		return self.connection.query_values(command)

	def write(self, command):
		""" Writes an SCPI command string to the instrument """
		self.connection.write(command)

	def read(self):
		""" Reads until the buffer is empty and returns the resulting ASCII response """
		return self.connection.read()

	def read_bytes(self, size):
		""" Reads specified number of bytes from the buffer and returns
		the resulting ASCII response

		:param size: Number of bytes to read from the buffer
		:returns: String ASCII response of the instrument.
		"""
		return self.connection.read_bytes(size)

	def binary_values(self, command, header_bytes=0, dtype=np.float32):
		""" Returns a numpy array from a query for binary data

		:param command: SCPI command to be sent to the instrument
		:param header_bytes: Integer number of bytes to ignore in header
		:param dtype: The NumPy data type to format the values with
		:returns: NumPy array of values
		"""
		self.connection.write(command)
		binary = self.connection.read_raw()
		header, data = binary[:header_bytes], binary[header_bytes:]
		return np.fromstring(data, dtype=dtype)

	def config(self, is_binary=False, datatype='str', container=np.array, converter='s',
			   separator=',', is_big_endian=False):
		""" Configurate the format of data transfer to and from the instrument.

		:param is_binary: If True, data is in binary format, otherwise ASCII.
		:param datatype: Data type.
		:param container: Return format. Any callable/type that takes an iterable.
		:param converter: String converter, used in dealing with ASCII data.
		:param separator: Delimiter of a series of data in ASCII.
		:param is_big_endian: Endianness.
		"""
		self.connection.values_format.is_binary = is_binary
		self.connection.values_format.datatype = datatype
		self.connection.values_format.container = container
		self.connection.values_format.converter = converter
		self.connection.values_format.separator = separator
		self.connection.values_format.is_big_endian = is_big_endian

	def wait_for_srq(self, timeout=25):
		""" Blocks until a SRQ, and leaves the bit high

		:param timeout: Timeout duration in seconds
		"""
		self.connection.wait_for_srq(timeout * 1000)
