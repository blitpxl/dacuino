from PySide6.QtWidgets import (
	QApplication,
	QWidget,
	QLabel,
	QVBoxLayout,
	QHBoxLayout,
	QPushButton,
	QLineEdit,
	QMessageBox,
	QComboBox
)
from PySide6.QtCore import (
	Qt,
	QThreadPool,
	Signal,
	QRunnable,
	QObject,
	QTimer,
	QUrl,
)
from bass import Bass, Flags
import platform
import serial
import ctypes
import time
import sys
import os


# professional logging system
def log(msg):
	print(f"LOG: {msg}")


class DataStreamerSignals(QObject):
	"""
	this class provides signals for DataStreamer, because signals can only
	by emitted by a class that inherits QObject. DataStreamer is QRunnable.
	"""

	stats_update = Signal(str)
	error_msg = Signal(str)
	track_end = Signal()


class DataStreamer(QRunnable):
	def __init__(self, buffer_sz, sample_rt, com_prt):
		super(DataStreamer, self).__init__()

		self.signals = DataStreamerSignals()

		self.running = False
		self.is_shut_down = True

		self.com_port = com_prt
		self.serial = None

		self.buffer_size = buffer_sz
		self.buffer = bytes(self.buffer_size)
		self.buffer_rd = self.buffer
		self.sample_rate = sample_rt
		self.sample_mono = False

		self.bass = Bass()
		self.bass.Init(0, -1, 0, 0, 0)

		log("loading basslibs.")
		if platform.system() == "Linux":
			log("detected linux platform.")
			self.bass.PluginLoad("lib/libbassflac.so".encode(), 0)
			self.bass.PluginLoad("lib/libbass_aac.so".encode(), 0)
		elif platform.system() == "Windows":
			log("detected win32 platform.")
			self.bass.PluginLoad("lib/bassflac.dll".encode(), 0)
			self.bass.PluginLoad("lib/bass_aac.dll".encode(), 0)
		self.stream = None
		self.mixer = None

		self.buffer_fill_count = 0
		self.bytes_sent = 0
		self.stats_update_timer = QTimer()
		self.stats_update_timer.setInterval(1000)
		self.stats_update_timer.timeout.connect(self.update_stats)
		self.signals.track_end.connect(self.stats_update_timer.stop)

	def update_stats(self):
		self.signals.stats_update.emit(f"buffer fills: {self.buffer_fill_count}/s, bytes sent: {self.bytes_sent}")
		self.buffer_fill_count = 0
		self.bytes_sent = 0

	def set_com_port(self, port):
		self.com_port = port
		log(f"set COM port to {port}.")

	def set_track(self, track):
		self.stream = self.bass.StreamCreateFile(False, track.encode(), 0, 0, Flags.STREAM_DECODE)
		if not self.sample_mono:
			self.mixer = self.bass.Mixer_StreamCreate(self.sample_rate, 2, Flags.STREAM_DECODE | Flags.SAMPLE_8BITS)
		else:
			self.mixer = self.bass.Mixer_StreamCreate(self.sample_rate, 1, Flags.STREAM_DECODE | Flags.SAMPLE_8BITS | Flags.SAMPLE_MONO)
		self.bass.Mixer_StreamAddChannel(self.mixer, self.stream, Flags.MIXER_NORAMPIN)
		self.bass.ChannelGetData(self.mixer, self.buffer, self.buffer_size)
		log(f"streaming {"mono" if self.sample_mono else "stereo"} track at {self.sample_rate}khz.")

	def enable(self):
		self.running = True
		self.is_shut_down = False
		if not self.stats_update_timer.isActive():
			self.stats_update_timer.start()
		log("streamer disabled.")

	def disable(self):
		self.running = False
		self.stats_update_timer.stop()
		log("streamer disabled.")

	def run(self):
		try:
			with serial.Serial(self.com_port) as ser:
				self.serial = ser
				ser.write(ctypes.c_uint16(self.sample_rate))
				ser.write(self.buffer)	# start filling first buffer
				while ser.read() and self.running:
					if self.bass.ChannelGetData(self.mixer, self.buffer, self.buffer_size) != 0:
						ser.write(self.buffer)
						self.buffer_fill_count += 1
						self.bytes_sent += self.buffer_size
					else:
						self.signals.track_end.emit()
						break
				ser.write(bytes(self.buffer_size*2))  # fill the dac buffer with zeros
			self.is_shut_down = True
		except Exception as e:
			log(e)
			self.signals.error_msg.emit(str(e))
			self.is_shut_down = True


class DropLabel(QLabel):
	on_drop_accept = Signal(str)

	def __init__(self, text, parent):
		super(DropLabel, self).__init__(text, parent)

	def dragEnterEvent(self, event):
		if event.mimeData().hasUrls():
			event.accept()

	def dropEvent(self, event):
		if event.mimeData().hasUrls():
			event.setDropAction(Qt.CopyAction)
			event.accept()
			self.on_drop_accept.emit(event.mimeData().urls()[0].toLocalFile())


class Window(QWidget):
	def __init__(self):
		super(Window, self).__init__()

		self.resize(700, 400)
		self.setWindowTitle("streamer")
		self.setObjectName("window")

		self.error_dialog = QMessageBox(self);

		# drag & drop receiver
		self.vbox = QVBoxLayout(self)
		self.vbox.setContentsMargins(0, 0, 0, 0)
		self.drop_receive_label = DropLabel("drop an audio file here", self)
		self.drop_receive_label.setWordWrap(True)
		self.drop_receive_label.setAlignment(Qt.AlignCenter)
		self.drop_receive_label.setAcceptDrops(True)
		self.drop_receive_label.setObjectName("drop-label")
		self.drop_receive_label.on_drop_accept.connect(self.on_track_drop)
		self.status_bar = QWidget(self)
		self.status_bar.setObjectName("status-bar")
		self.status_bar.setFixedHeight(24)

		self.vbox.addWidget(self.drop_receive_label)
		self.vbox.addWidget(self.status_bar)

		# status bar
		self.hbox = QHBoxLayout(self.status_bar)
		self.hbox.setContentsMargins(4, 0, 4, 0)
		self.stats = QLabel("standing by...", self.status_bar)
		self.stats.setObjectName("stats")

		self.sample_rate_label = QLabel("sample rate:", self.status_bar)
		self.sample_rate_label.setObjectName("stats")
		self.sample_rate_input = QLineEdit("8000", self.status_bar)
		self.sample_rate_input.setFixedWidth(100)
		self.sample_rate_input.returnPressed.connect(self.on_sample_rate_set)
		self.com_port_select = QComboBox(self.status_bar)

		if platform.system() == "Linux":
			self.com_port_select.addItems([f"/dev/ttyACM{i}"for i in range(0, 10)])
		elif platform.system() == "Windows":
			self.com_port_select.addItems([f"COM{i}"for i in range(0, 10)])

		self.hbox.addWidget(self.stats)
		self.hbox.addStretch()
		self.hbox.addWidget(self.sample_rate_label)
		self.hbox.addWidget(self.sample_rate_input)
		self.hbox.addWidget(self.com_port_select)

		self.threadpool = QThreadPool(self)

		self.streamer = DataStreamer(1196, int(self.sample_rate_input.text()), self.com_port_select.currentText())	# buffer size, sample rate
		self.streamer.setAutoDelete(False)
		self.streamer.signals.stats_update.connect(self.on_stats_update)
		self.streamer.signals.error_msg.connect(self.on_error)
		self.streamer.signals.track_end.connect(self.on_track_end)
		self.com_port_select.currentTextChanged.connect(lambda selected: self.streamer.set_com_port(selected))

	def on_error(self, msg):
		self.error_dialog.setIcon(QMessageBox.Icon.Critical)
		self.error_dialog.setWindowTitle("Error")
		self.error_dialog.setText(msg)
		self.error_dialog.show()

	def on_sample_rate_set(self):
		try:
			self.streamer.disable()

			# wait for streamer to shut down, but don't wait too long
			i = 0
			while not self.streamer.is_shut_down and i < 30:
				i += 1
				time.sleep(1)
			self.streamer.sample_rate = int(self.sample_rate_input.text())
			with serial.Serial(self.streamer.com_port, 1200):	# reset (https://github.com/sudar/Arduino-Makefile/issues/30)
				pass
		except Exception as e:
			log(e)
			self.on_error(str(e))

	def on_stats_update(self, stats):
		self.stats.setText(stats)

	def on_track_end(self):
		self.drop_receive_label.setText("drop an audio file here")
		self.stats.setText("standing by...")

	def on_track_drop(self, path):
		if self.streamer.is_shut_down:
			self.streamer.set_track(path)
			self.streamer.enable()
			self.threadpool.start(self.streamer)
			self.drop_receive_label.setText(os.path.splitext(os.path.basename(path))[0])
		else:
			self.streamer.disable()
			while not self.streamer.is_shut_down:	# wait for streamer to shutdown
				pass
			self.on_track_drop(path)
			
	def closeEvent(self, event):
		self.streamer.disable()


app = QApplication(sys.argv)
app.setStyleSheet(
	"QWidget#window {background: #202020;} \
	QWidget#status-bar {background: #BDBDBD;} \
	QLabel#drop-label {color: rgba(255, 255, 255, 128); font-family: consolas; font-size: 18px;} \
	QLabel#stats {color: rgba(0, 0, 0, 156); font-family: consolas; font-size: 14px;}"
)
win = Window()
win.show()
sys.exit(app.exec())