from multiprocessing import get_context

context = get_context()
# Useful for multiprocessing debugging:
# context.log_to_stderr(logging.DEBUG)


class StoppableProcess(context.Process):
	""" Base class for Processes which require the ability
	to be stopped by a process-safe method call
	"""

	def __init__(self):
		super().__init__()
		self._should_stop = context.Event()
		self._should_stop.clear()

	def join(self, timeout=0):
		""" Joins the current process and forces it to stop after
		the timeout if necessary

		:param timeout: Timeout duration in seconds
		"""
		self._should_stop.wait(timeout)
		if not self.should_stop():
			self.stop()
		return super().join(0)

	def stop(self):
		self._should_stop.set()

	def should_stop(self):
		return self._should_stop.is_set()

	def __repr__(self):
		return "<%s(should_stop=%s)>" % (
			self.__class__.__name__, self.should_stop())