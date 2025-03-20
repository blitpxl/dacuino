import serial

BUFFER_SIZE = 2300

idx_start = 0
idx_end = BUFFER_SIZE

with open("build/samples", "rb") as file:
	data = bytearray(file.read())
	with serial.Serial("/dev/ttyACM0", 500000) as ser:
		while True:
			ser.read()
			buffer = data[idx_start:idx_end]
			ser.write(buffer)
			idx_start = idx_end
			idx_end += BUFFER_SIZE