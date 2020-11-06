from Instruments.instrument import Instrument
import numpy as np
import time

class FireBERD(Instrument):
	models = ["FB"]
	def __init__(self, name, adapter, **kwargs):
		super(FireBERD, self).__init__(name, adapter, **kwargs)
		self.write('\x03') # Initialize the COM port

	def close(self):
		self.rts(False) # unkey before closing
		super(Fireberd6000A,self).close()

	def reset(self):
		self.rts(False)
		self.write('RESULT:RESTART')
		self.write('*CLS')		

	def restart(self):
		self.write('RESULT:RESTART')

	def rts(self,on=None):
		if on is not None:
			self.write('CONFIG:RTS %s'%('ON' if on else 'OFF'))
			time.sleep(1)
		else:
			result = self.query('CONFIG:RTS?')
			return {'ON':True,'OFF':False}[result]

	def tpz(self,on=None):
		if on is not None:
			self.write('CONFIG:TPZ %s'%('ON' if on else 'OFF'))
			time.sleep(0.5)
		else:
			result = self.query('CONFIG:TPZ?')
			return {'ON':True,'OFF':False}[result]
		
	## config

	def genDataInv(self,invert=None):
		if invert is not None:
			self.write('AUX:GEN_DATA_INV %s'%('ON' if invert else 'OFF'))
		else:
			result = self.query('AUX:GEN_DATA_INV?')
			return {'ON':True,'OFF':False}[result]

	Patterns = [ 'MARK', '1:1', '63', '511', '2047', '2^15-1', '2^20-1', '2^23-1', 
				 'QRSS', 'PRGM', 'FOX', 'USER' ]
	def pattern(self,pattern=None):
		if pattern is not None:
			if pattern not in Fireberd6000A.Patterns:
				raise Exception('Invalid Pattern: %s'%pattern)
			self.write('CONFIG:PATTERN %s'%pattern)
		else:
			result = self.query('CONFIG:PATTERN?')
			if result not in Fireberd6000A.Patterns:
				raise Exception('Invalid Pattern: %s'%result)
			return result

	def prgmPattern(self,pattern=None):
		if pattern is not None:
			self.write('AUX:PRGM_PATTERN %s'%pattern)
		else:
			result = self.query('AUX:PRGM_PATTERN?')
			return result

	def blockLen(self,length=None):
		if length is not None:
			self.write('AUX:BLOCK_LEN %d'%length)
		else:
			result = self.query('AUX:BLOCK_LEN?')
			return int(result)

	## results

	def ber(self):
		result = self.query('RESULT? BER')
		return float(result)

	def avgBer(self):
		result = self.query('RESULT? AVG_BER')
		return float(result)
		
	def bitErrors(self):
		result = self.query('RESULT? BIT_ERRS')
		return int(result)

	def patSlips(self):
		result = self.query('RESULT? PAT_SLIP')
		return int(result)

	def clkLoss(self):
		result = self.query('RESULT? CLK_LOSS')
		return int(result)

	def patLoss(self):
		result = self.query('RESULT? PAT_LOSS')
		return int(result)

	def blocks(self):
		result = self.query('RESULT? BLOCKS')
		return int(result)

	def genFreq(self):
		result = self.query('RESULT? GEN_FREQ')
		try:
			return float(result.replace('"',''))
		except:
			return 0.0

	def rcvFreq(self):
		result = self.query('RESULT? RCV_FREQ')
		try:
			return float(result.replace('"',''))
		except:
			return 0.0

	def elapsedTime(self):
		result = self.query('RESULT? ELAP_SEC')
		return int(result)

	# status

	# STATUS:LINE? Query returns an 8 bit register:
	# bit 8 (MSB): Not used, always 0
	# bit 7: TEST COMPLETE
	# bit 6: RCV CLK INV (True when inverted clock is received)
	# bit 5: RCV DATA INV (True when inverted data is received)
	# bit 4: GEN CLK PRES (True when generated clock is present)
	# bit 3: PATTERN SYNC
	# bit 2: FRAME SYNC
	# bit 1 (LSB): SIGNAL PRESENT

	# STATUS:INTF? Query returns an 8 bit register:
	# bit 8 (MSB): Not used, always 0
	# bit 7: Not used, always 0
	# bit 6: DSR/DTR (User assertable in DTE emulation)
	# bit 5: RLSD/RTS (User assertible in DTE emulation)
	# bit 4: RL/TM
	# bit 3: LL/CTS
	# bit 2: DTR/DSR (User assertable in DCE emulation)
	# bit 1 (LSB): RTS/RLSD (User assertable in DCE emulation)

	def rlsd(self):
		result = self.query('STATUS:INTF?')
		flag = int(result) & 0x01
		return flag>0

	def sigPres(self):
		result = self.query('STATUS:LINE?')
		flag = int(result) & 0x01
		return flag>0

	def patSync(self):
		result = self.query('STATUS:LINE?')
		flag = int(result) & 0x04
		return flag>0

	def dataInv(self):
		result = self.query('STATUS:LINE?')
		flag = int(result) & 0x10
		return flag>0

	def cts(self):
		result = self.query('STATUS:INTF?')
		flag = int(result) & 0x04
		return flag>0

	def genClk(self):
		result = self.query('STATUS:LINE?')
		flag = int(result) & 0x08
		return flag>0

	# overrides

	def write(self, msg, readErrors=True):
		super(Fireberd6000A,self).write(msg, readErrors)
		self.read() # get the echo

	def read(self, returnType='string'):
		# Override 
		result = super(Fireberd6000A,self).read(returnType)
		return result.strip().encode('utf8')

### UNIT TEST ##################################################################
if __name__ == '__main__':
	fireberd = Fireberd6000A('ASRL17::INSTR')

	fireberd.reset()

	fireberd.rts(True)
	print('rts',fireberd.rts())
	time.sleep(1)
	fireberd.rts(False)
	print('rts',fireberd.rts())

	print('### Config...')
	print('genDataInv',fireberd.genDataInv())
	try:
		fireberd.pattern('123')
	except Exception as e:
		print(e)
	fireberd.pattern('63')
	print('pattern',fireberd.pattern())
	print('prgmPattern',fireberd.prgmPattern())

	print('')
	print('### Results...')
	print('ber',fireberd.ber())
	print('avgBer',fireberd.avgBer())
	print('bitErrors',fireberd.bitErrors())
	print('patSlips',fireberd.patSlips())
	print('clockLoss',fireberd.clockLoss())
	print('patLoss',fireberd.patLoss())
	print('blocks',fireberd.blocks())
	print('genFreq',fireberd.genFreq())
	print('rcvFreq',fireberd.rcvFreq())
	print('elapsedTime',fireberd.elapsedTime())

	print('')
	print('### Status...')
	print('rlsd',fireberd.rlsd())
	print('sigPres',fireberd.sigPres())
	print('patSync',fireberd.patSync())
	print('dataInv',fireberd.dataInv())
	print('cts',fireberd.cts())
	print('genClk',fireberd.genClk())

	print('')
	print('### Test...')
	fireberd.rts(True)
	print('rts',fireberd.rts())
	fireberd.restart()
	time.sleep(2)

	print('')
	print('ber',fireberd.ber())
	print('avgBer',fireberd.avgBer())
	print('bitErrors',fireberd.bitErrors())
	print('patSlips',fireberd.patSlips())
	print('clockLoss',fireberd.clockLoss())
	print('patLoss',fireberd.patLoss())
	print('blocks',fireberd.blocks())
	print('genFreq',fireberd.genFreq())
	print('rcvFreq',fireberd.rcvFreq())
	print('elapsedTime',fireberd.elapsedTime())

	print('')
	print('rlsd',fireberd.rlsd())
	print('sigPres',fireberd.sigPres())
	print('patSync',fireberd.patSpythnync())
	print('dataInv',fireberd.dataInv())
	print('cts',fireberd.cts())
	print('genClk',fireberd.genClk())

	fireberd.rts(False)
