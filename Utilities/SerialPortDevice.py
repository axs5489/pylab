"""
 SerialPortDevice: ASCII Serial Port class
"""
import serial
import time
import re
import threading
import Queue
import win32pipe
import win32file
import logging

class SerialPipe(object):
	""" This class mimics the python serial interface, but instead of 
		reading/writing data to a physical Serial Port device, it 
		reads/writes to the device through a proxy via a Named Pipe. 
		
		This is used in conjunction with the SerialProxy program which
		actually connects to the physical Serial Port and then provides
		multiple connections via a named pipe (\\.\pipe\COMx).
		"""
	def __init__(self,name,timeout,logger):
		self.handle = win32file.CreateFile(name,
				  win32file.GENERIC_READ | win32file.GENERIC_WRITE,
				  0, None, win32file.OPEN_EXISTING, 0, None)
		self.timeout = timeout
		self.logger = logger

	def close(self):
		""" Closes the Serial Port Pipe. """
		win32file.CloseHandle(self.handle)
		self.handle = None

	def write(self, data):
		""" Writes data to the Serial Port Pipe. """
		win32file.WriteFile(self.handle, data)

	def readline(self):
		""" Reads a single line from the Serial Port Pipe. """
		if self.timeout > 0:
			start_time = time.time()
			total_num_bytes = 0
			while (time.time() - start_time) < self.timeout:
				(pipeData,numBytes,unused)=win32pipe.PeekNamedPipe(self.handle,4096)
				if numBytes>0:
					# look for the line-end. if found, read up to (and including) the line-end
					# if never found and we time-out, just read everything available...
					lineEndIdx = pipeData.find('\n')
					if( lineEndIdx >= 0 ):
						numBytes = lineEndIdx + 1
						break

					# if we did get some NEW bytes (but still no newline), reset the start-time 
					# so that we don't prematurely give up if there's more data coming
					if numBytes > total_num_bytes:
						total_num_bytes = numBytes
						start_time = time.time()
				time.sleep(0.1)
		else:
			(pipeData,numBytes,unused)=win32pipe.PeekNamedPipe(self.handle,4096)

		if numBytes>0:
			data = win32file.ReadFile(self.handle, numBytes)
			line = data[1]
		else:
			line = ''
		#self.logger.debug( "RX[P]: '%s'" % (line))
		return line
	 
	def flushInput(self):
		""" Flush's the Serial Port Pipe receive buffer. """
		# TBD: Don't do this since it has threading issues which cause us to 
		#	  block indefinitely. Instead, rely on the async Queue flush to handle this.
		#(pipeData,numBytes,unused)=win32pipe.PeekNamedPipe(self.handle,4096)
		#if numBytes>0:
		#	data = win32file.ReadFile(self.handle, numBytes)
		pass


def serial_receive_func(handle,q,stop,logger):
	""" This is the Asynchronous serial port read thread handler function. """
	while True:
		# Read a line from the serial port
		# If there is no data available, this will timeout after handle.timeout
		# seconds and return ''.
		try:
			s = handle.readline()
		except Exception as e:
			logger().exception( "Error reading from serial port!: %r", e)
			s = None
		
		# If the read returned a line, then add it to the queue
		# and log the line. Do some checking to roll old messages off the 
		# end of the queue if necessary.
		if s:
			if q.full():
				logger().debug( "throwing away oldest recv data..." )
				q.get()
			q.put(s.strip())
			logger().debug( "RX[%d]: '%s'" % (q.qsize(),s.strip()))
		else:
			time.sleep(1)

		# Call the stop function to see if the parent thread is trying to
		# terminate this helper thread
		if stop():
			break

class SerialPortDevice(object):
	""" This class encapsulates an ASCII Serial Port and provides 2 distinct
		modes of read operation:
			1) Synchronous: All physical serial port hardware reads are handled 
				synchronously on the caller thread.
			2) Asynchronous: All physical reads are handled by a background 
				helper thread, which logs and buffers the data. Users of the 
				SerialPortDevice read data synchronously on the caller's thread 
				from this buffer (and not the serial port hardware directly). 
				Using this mode, all data received from the serial port can be 
				logged, and long delays between when the physical data comes in 
				and when the caller gets the data are possible without losing data.
			Note that all writes are synchronous.
	"""
	class Timeout(Exception):
		""" Exception signifying a serial port read/wait Timeout. """
		pass

	class ThreadLockTimeout(Exception):
		"""	Exception signifying a thread was blocked from getting access to the serial device"""
		pass

	def __init__(self,port,async=False,baud=115200,name=None,tx_term='\n',echos=True):
		""" SerialPortDevice Constructor.
				port: a "COMn" string
				async: True=use an asynchronous background thread for all reads
				baud: the baud rate to use
				name: an optional name to use for logging
				tx_term: tx terminator string
				echos: True if this port echos Tx messages back, False if it does not
		"""
		if not name:		
			name = port # if no name provided, just use the port name

		self.logger = logging.getLogger("Serial(%s)"%name)
		#self.logger.debug(self.__init__.__name__)

		# Try to open the Serial Port. First, open it directly. If this 
		# failes, then attempt to open it via the Proxy named pipe. If that
		# also fails, throw the error.
		try:
			self.handle = serial.Serial(port=port, baudrate=baud, bytesize=8, 
				parity="N", stopbits=1, timeout=3.0, writeTimeout=3.0, xonxoff=0, rtscts=0)
		except Exception as e:
			self.logger.debug("Couldn't connect directly to %s - %s"%(port,e))
			try:
				self.handle = SerialPipe(r'\\.\pipe\%s'%port, timeout=3.0, logger=self.logger)
			except:
				raise Exception("Error opening Serial Port: %s!!" % port)

		self.tx_terminator = tx_term #'\n'
		self.echos = echos

		# If Asynchronous, setup and start the helper thread
		# Pass a lambda function that just returns the stop flag to support 
		# stopping the thread.
		self.async = async
		if self.async:
			self.q = Queue.Queue(maxsize=4096)

			self.stop = False
			self.t = threading.Thread(target=serial_receive_func, args=(self.handle, self.q, lambda:self.stop, lambda:self.logger))
			# Make the thread a Daemon so that we don't hang at the end of a 
			# script if we forget to close the Serial Port
			self.t.daemon = True
			self.t.start()
			
		self.port = port
		self._lock = threading.RLock()  # re-entrant lock object for thread safe writes
		self.logger.debug("SerialPortDevice: Port Opened: %s"%(self.port))


	def __del__(self):
		self.close()

	def close(self):
		""" Closes the serial port and stops the Asynchronous read-thread. """
		if hasattr(self,'async') and self.async:
			self.stop = True
			self.t.join()
		if hasattr(self,'handle'):
			self.handle.close()
		if hasattr(self,'port'):
			print("SerialPortDevice: Port Closed: %s"%(self.port))

	def send(self,sendStr):
		""" Writes the given string to the serial port. """
		self._get_mutex()
		self.logger.debug("TX: '%s'" % sendStr.strip())
		try:
			self.handle.write((sendStr + self.tx_terminator).encode())
		except serial.writeTimeoutError:
			# write() timed-out for some reason - try to send another 
			# tx_terminator to see if that gets things through... if not,
			# then, we'll just except again
			self.logger.warning("Tx Write Timeout!! Trying again...")
			self.handle.write(self.tx_terminator.encode())
		finally:
			self._release_lock()

	def recv(self):
		""" Reads a line from the serial port. """
		#self.logger.debug(self.recv.__name__)

		# If Asynchronous, read from the Queue (that is filled by the read
		# thread). If Synchronous, read from the serial port directly.
		if self.async:
			try:
				return self.q.get(timeout=self.handle.timeout)
			except Queue.Empty:
				return ''
		else:
			s = self.handle.readline()
			self.logger.debug( "RX: '%s'" % (s.strip()))
			return s

	def send_and_wait(self,sendStr,waitStr,timeout=10,timeoutException=True,useRegex=False,caseSensitive=False):
		""" Writes a string to the serial port, then waits for the given 
			response string. If the response timesout (after 'timeout' seconds),
			an exception is thrown.
				sendStr: string to write to the serial port
				waitStr: sub string or regex to wait on (if this string matches
						 any part of a read line, return)
				timeout: timeout in seconds
				timeoutException: if True and timed-out, raise the Timeout 
						 exception; otherwise return ''
				useRegex: if True, treat waitStr as a regex expression; if false
						 treat it normally (regex expressions are ignored)
				caseSensitive: if True, the wait is case-sensitive
			Returns the full line containing the waitStr (or '' if timed-out 
				and timeoutException==False)
		"""
		#self.logger.debug(self.send_and_wait.__name__ + "('%s','%s',%d)" % (sendStr,waitStr,timeout))

		self._get_mutex()
		self.flush_recv()
		self.send(sendStr)

		# If this port supports echo'ing of the sends, wait for the read-back
		# before continuing.
		if self.echos:
			self.waitfor(sendStr.strip(),timeout,False,False)

		try:
			return self.waitfor(waitStr,timeout,timeoutException,useRegex,caseSensitive)
		except SerialPortDevice.Timeout:
			raise SerialPortDevice.Timeout("SerialPortDevice.send_and_wait() timed out. Command: '%s', waited for: '%s'" % (sendStr, waitStr))
		finally:
			self._release_lock()

	def flush_recv(self):
		""" Flushes the serial port's receive buffer. """
		#self.logger.debug(self.flush_recv.__name__)

		# If Asynchronous, drain the Queue until it is empty.
		# Otherwise, directly Flush the serial port.
		if self.async:
			try:
				loopcount = 10e3 # safety feature
				while loopcount>0:
					if self.q.empty():
						break
					self.q.get_nowait()
					loopcount -= 1
				else:
					self.logger.warning("flush_recv timed out! (qsize=%s)!"%self.q.qsize())
			except Queue.Empty:
				pass
		else:
			self.handle.flushInput()

	def waitfor(self,waitStr,timeout=10,timeoutException=True,useRegex=False,caseSensitive=False):
		""" Reads from the serial port until waitStr is matched.
				waitStr: sub string or regex to wait on (if this string matches
						 any part of a read line, return)
				timeout: timeout in seconds
				timeoutException: if True and timed-out, raise the Timeout 
						 exception; otherwise return ''
				useRegex: if True, treat waitStr as a regex expression; if false
						 treat it normally (regex expressions are ignored)
				caseSensitive: if True, the wait is case-sensitive
			Returns the full line containing the waitStr (or '' if timed-out 
				and timeoutException==False)
		"""
		#self.logger.debug(self.waitfor.__name__ + "('%s',%d,%s)" % (waitStr,timeout,useRegex))

		start_time = time.time()

		if useRegex:
			rg = re.compile(waitStr,re.IGNORECASE if not caseSensitive else 0)
			while (time.time() - start_time) < timeout:
				s = self.recv()
				#print s
				if s is not None:
					m = rg.search(s)
					if m:
						return s.strip()
		else:
			while (time.time() - start_time) < timeout:
				s = self.recv()
				if s is not None:
					if caseSensitive:
						if s.find(waitStr) >= 0:
							return s.strip()
					else:
						if s.lower().find(waitStr.lower()) >= 0:
							return s.strip()

		errorStr = "SerialPortDevice.waitfor() timed out waiting for '%s'" % waitStr
		if timeoutException:
			raise SerialPortDevice.Timeout(errorStr)
		else:
			self.logger.debug(errorStr) # not an error, but do log it
			return ''

	def lock(self, timeout=15):
		"""
		Method to lock a serial port device so that atomic writes can be performed.  The lock is re-entrant so the
		thread that owns the lock can perofrm writes on the serial device any number of times.

		Args:
			timeout (sec): Time to wait while trying to acquire the mutex
		"""
		self.logger.debug("Locking serial port")
		self._get_mutex(timeout)

	def release(self):
		"""
		Method to release a lock on the serial device
		"""
		self.logger.debug("Releasing serial port lock")
		self._release_lock()

	def _get_mutex(self, timeout=10):
		"""
		Private method to get mutex lock prior to writing data to serial port.  This call is blocking.

		Args:
			timeout (int): Number of seconds to wait before throwing Timeout exception

		Raises:
			Timeout
		"""
		attempts = 0
		wait_time = 0.1	 # seconds
		elapsed_time = 0
		start_time = time.time()
		lock_status = self._lock.acquire(0)  # attempt to get the lock
		if lock_status:
			return
		else:
			# another thread locked the serial port so we'll wait and try again
			while not lock_status:

				elapsed_time = time.time() - start_time
				if elapsed_time > timeout:
					raise SerialPortDevice.ThreadLockTimeout("Timed out waiting for mutex")
				else:
					time.sleep(wait_time)
					attempts += 1
					lock_status = self._lock.acquire(0)

			self.logger.debug("Mutex acquired after %d attempts (%.2f seconds)" % (attempts, elapsed_time))

	def _release_lock(self):
		self._lock.release()
