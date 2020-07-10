from .adapter import Adapter
import numpy as np
import serial

class SerialAdapter(Adapter):
	""" Adapter class for using the Python Serial package to allow
	serial communication to instrument
	:param port: Serial port
	:param kwargs: Any valid key-word argument for serial.Serial
	"""
	def __init__(self, port, **kwargs):
		if isinstance(port, serial.Serial):
			self.connection = port
		else:
			self.connection = serial.Serial(port, **kwargs)

	def __del__(self):
		""" Ensures the connection is closed upon deletion """
		self.connection.close()

	def write(self, command):
		""" Writes an SCPI command string to the instrument """
		self.connection.write(command.encode())  # encode added for Python 3

	def read(self):
		""" Reads until the buffer is empty and returns the resulting ASCII respone """
		return b"\n".join(self.connection.readlines()).decode()

	def binary_values(self, command, header_bytes=0, dtype=np.float32):
		""" Returns a numpy array from a query for binary data 

		:param command: SCPI command to be sent to the instrument
		:param header_bytes: Integer number of bytes to ignore in header
		:param dtype: The NumPy data type to format the values with
		:returns: NumPy array of values
		"""
		self.connection.write(command.encode())
		binary = self.connection.read().decode()
		header, data = binary[:header_bytes], binary[header_bytes:]
		return np.fromstring(data, dtype=dtype)

	def __repr__(self):
		return "<SerialAdapter(port='%s')>" % self.connection.port
