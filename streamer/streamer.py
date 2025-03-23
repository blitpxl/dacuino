import threading
import serial
import ctypes
import time
import sys

BUFFER_SIZE = 1024

idx_start = 0
idx_end = BUFFER_SIZE

buffer_reqs = 0
byte_sent = 0

def stat():
	while True:
		global buffer_reqs
		global byte_sent
		print(f"Buffer fill requests: {buffer_reqs*2}/s\nByte sent: {byte_sent*2}/s")
		buffer_reqs = 0
		byte_sent = 0
		time.sleep(0.5)

threading.Thread(target=stat).start()

with open("build/samples", "rb") as file:
	data = bytearray(file.read())
	data_len = len(data)
	try:
		with serial.Serial("/dev/ttyACM0", 500000) as ser:
			ser.write(ctypes.c_ushort(48000))

			# fill init buffer
			buffer = data[idx_start:idx_end]
			ser.write(buffer)
			while True:
				ser.read()
				buffer = data[idx_start:idx_end]
				ser.write(buffer)
				idx_start = idx_end
				idx_end += BUFFER_SIZE
				buffer_reqs += 1
				byte_sent += BUFFER_SIZE
				if idx_start >= data_len:
					ser.write([0 for _ in range(BUFFER_SIZE)])
	except serial.SerialException as e:
		print(f"Serial error ({e}) Retrying...")