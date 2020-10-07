from Utilities.SerialPort import SerialPort
import time

# COM1=117G red side
# COM3=117G black side
Port1 = "COM6"
Port2 = "COM7"
TestList = [0,1,2,3,4,5]

# Test 0: documentation
if 0 in TestList:
	help(SerialPort)

# Test 1: asynchronous operation
if 1 in TestList:
	print("Creating Asynchronous SerialPort object.")
	ser = SerialPort("Port 1", Port1,True)

	ser.send("ls /")
	time.sleep(1)
	try:
		ser.send_and_wait("pwd","shmem",3,True)
	except SerialPort.Timeout:
		print("timed out, why??")

	try:
		ser.send_and_wait("pwd","sdfd",3,True)
	except SerialPort.Timeout:
		print("timed out, this was expected.")

	try:
		ser.waitfor("12345")
	except SerialPort.Timeout:
		print("timed out, this was also expected.")

	print("Closing Asynchronous SerialPort object.")
	ser.close()
	del ser

# Test 2: synchronous operation
if 2 in TestList:
	print("Creating Synchronous SerialPort object.")
	ser = SerialPort(Port1,False)

	ser.send("ls /")
	time.sleep(1)
	try:
		ser.send_and_wait("pwd","shmem",3,False)
	except SerialPort.Timeout:
		print("timed out, why??")

	print("Closing Synchronous SerialPort object.")
	ser.close()
	del ser

# Test 3: parallel asynchronous operation
if 3 in TestList:
	print("Creating Synchronous SerialPort objects.")
	ser1 = SerialPort("Port 1", Port1, True)
	ser2 = SerialPort("Port 2", Port2, True)

	try:
		ser1.send_and_wait("pwd","shmem",3,True)
	except SerialPort.Timeout:
		print("timed out, why??")

	time.sleep(3)

	try:
		ser2.send_and_wait("pwd","shmem",3,True)
	except SerialPort.Timeout:
		print("timed out, why??")

	print("Closing Synchronous SerialPort objects.")
	ser1.close()
	ser2.close()
	del ser1
	del ser2

# Test 4: reset radio and capture both outputs
if 4 in TestList:
	print("Creating Synchronous SerialPort objects.")

	ser1 = SerialPort("Port 1", Port1,True)
	ser2 = SerialPort("Port 2", Port2,True)

	print("Rebooting Radio and waiting....")
	ser2.send_and_wait("ascii",">")
	ser2.send("reset")

	a=ser1.waitfor("#",60,False)
	print("Reboot Result 1: '%s'" % a)
	a=ser2.waitfor("#",60,False)
	print("Reboot Result 2: '%s'" % a)

	print("Closing Synchronous SerialPort objects.")

	ser1.close()
	ser2.close()
	del ser1
	del ser2

# Test 5: Logger Test
if 5 in TestList:

	print("Creating Asynchronous SerialPort object.")
	ser = SerialPort(Port1,False)
	ser2 = SerialPort(Port2,True,name="Radio1Red")

	#ser.send("ls /")
	ser.send_and_wait("pwd","#",3)
	ser2.send("ls /bin")
	time.sleep(1)
	ser2.recv()

	print("Closing Asynchronous SerialPort object.")
	#ser.close()
	del ser
	ser2.close()
	del ser2