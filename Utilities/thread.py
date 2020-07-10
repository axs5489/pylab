from threading import Thread, Event
import time

class StoppableThread(Thread):
	""" Base class for Threads which require the ability
	to be stopped by a thread-safe method call
	"""

	def __init__(self, target=None, args=(), kwargs=None):
		self.target = target
		self.args = args
		self.kwargs = kwargs
		super(StoppableThread, self).__init__(group=group, target=target, name=name, args=args, kwargs=kwargs)
		self._stop_event = Event()
		self._stop_event.clear()

	def join(self, timeout=0, *args, **kwargs):
		""" Joins the current thread and forces it to stop after
		the timeout if necessary

		:param timeout: Timeout duration in seconds
		"""
		self._stop_event.wait(timeout)
		if not self.should_stop():
			self.stop()
		return super(StoppableThread, self).join(0, *args, **kwargs)

	def stop(self):
		self._stop_event.set()
	
	def is_stopped(self):
		"""	Method to check if the thread is stopped. """
		stopped = False
		if self._stop_event.is_set():
			stopped = True
		return stopped

	def should_stop(self):
		return self._stop_event.is_set()

	def __repr__(self):
		return "<%s(should_stop=%s)>" % (
			self.__class__.__name__, self.should_stop())

class DroneThread(StoppableThread):
	""" Stoppable thread that runs a target function in a loop. """

	def __init__(self, group=None, target=None, name=None, args=(), kwargs=None):
		"""
		Drone thread that will run a function on a separate, stoppable thread.  Signature follows threading.Thread.
		Args:
			group:
			target:
			name:
			args:
			kwargs:

		Keyword Args:
			LoopDelay (int): Time in seconds to delay between calls to target function
			InitDelay (int): Initial delay before first call to target function
		"""
		self._loopdelay = kwargs.pop('LoopDelay', 1)
		self._initdelay = kwargs.pop('InitDelay', 0)

		super(DroneThread, self).__init__(group=group, target=target, name=name, args=args, kwargs=kwargs)

	def run(self):
		""" Start drone loop - runs target function every (LoopDelay) seconds until the stop() method is called. """
		if self.target:
			time.sleep(self._initdelay)
			while not self._stop_event.is_set():
				self.target(*self.args, **self.kwargs)  # run the target function
				time.sleep(self._loopdelay)