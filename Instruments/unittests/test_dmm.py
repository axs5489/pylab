import unittest
from Adapters.visa import VISAAdapter
from Instruments.dmm import DMM

class TestDMM(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		print('setupClass')
		cls.adptr = VISAAdapter("DMM", "GPIB0::7::INSTR")

	@classmethod
	def tearDownClass(cls):
		print('teardownClass')

	def setUp(self):
		print('setUp')
		self.instr = DMM("DMM", self.adptr)
		self.instr.clear()
		input()

	def tearDown(self):
		print('tearDown\n')
		if(self.instr.check_errors()):
			print('TEARDOWN ERROR!')

	def test_beep(self):
		print('test_beep')
		self.instr.beep()

	def test_cap(self):
		print('test_cap')
		print(self.instr.capacitance)

	def test_cont(self):
		print('test_cont')
		print(self.instr.continuity)

	def test_diode(self):
		print('test_diode')
		print(self.instr.diode)

	def test_freq(self):
		print('test_freq')
		print(self.instr.freq)

	def test_per(self):
		print('test_per')
		print(self.instr.period)

	def test_current(self):
		print('test_current')
		print(self.instr.current_ac)
		print(self.instr.current_dc)

	def test_voltage(self):
		print('test_voltage')
		print(self.instr.voltage_ac)
		print(self.instr.voltage_dc)

	def test_res(self):
		print('test_res')
		print(self.instr.resistance)
		print(self.instr.resistance_4w)

	def test_temp(self):
		print('test_temp')
		print(self.instr.temp)
		
		print(self.instr.temp_4w)

	def test_modes(self):
		print('test_modes')
		for m in self.instr.functions:
			self.instr.write('FUNC "{}"'.format(m))
			if(self.instr.check_errors()):
				print('ERROR: ', m)
			input()
			self.instr.clear()

if __name__ == '__main__':
	unittest.main()