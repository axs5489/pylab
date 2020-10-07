import threading
import time
from Utilities.SerialPortDevice import SerialPortDevice

#Test script to checkout multi-threading capability of SerialPortDevice

def thread1():
	for x in range(0,5):
		serialPort.lock()
		serialPort.send("Thread1 Message")
		time.sleep(1)
		serialPort.release()
		time.sleep(10)

def thread2():
	for x in range(0,5):
		time.sleep(5)
		serialPort.send("Thread2 Message")


if __name__=="__main__":
	serialPort = SerialPortDevice('COM6',True)

	t1 = threading.Thread(name='Thread1',target=thread1)
	t2 = threading.Thread(name='Thread2',target=thread2)

	t1.start()
	t2.start()

	t1.join()
	t2.join()