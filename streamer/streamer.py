import serial
import ctypes
import enum
import time
import sys

RAW_SAMPLES = "/home/blitpxl/Documents/Billie Eilish - when the party's over.raw"
BUFFER_SIZE = 1024

idx_start = 0
idx_end = BUFFER_SIZE

with open(RAW_SAMPLES, "rb") as file:
	data = file.read()
	data_len = len(data)
	try:
		with serial.Serial("/dev/ttyACM0") as ser:
			ser.write(data[idx_start:idx_end])
			idx_start = idx_end
			idx_end += BUFFER_SIZE

			while True:
				message = ser.read()
				buffer = data[idx_start:idx_end]
				ser.write(buffer)
				idx_start = idx_end
				idx_end += BUFFER_SIZE
				if idx_end >= data_len:
					[0 for _ in range(BUFFER_SIZE)]
	except serial.SerialException as e:
		print(f"Serial error ({e}) Retrying...")