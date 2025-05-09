from ctypes import cdll
import platform


class Flags:
	UNICODE 			= 0x80000000

	SAMPLE_8BITS		= 1
	SAMPLE_FLOAT		= 256
	SAMPLE_MONO			= 2
	SAMPLE_LOOP			= 4
	SAMPLE_3D			= 8
	SAMPLE_SOFTWARE		= 16
	SAMPLE_MUTEMAX		= 32
	SAMPLE_VAM			= 64
	SAMPLE_FX			= 128
	SAMPLE_OVER_VOL		= 0x10000
	SAMPLE_OVER_POS		= 0x20000
	SAMPLE_OVER_DIST	= 0x30000

	STREAM_PRESCAN		= 0x20000 
	STREAM_AUTOFREE		= 0x40000	
	STREAM_RESTRATE		= 0x80000	
	STREAM_BLOCK		= 0x100000
	STREAM_DECODE		= 0x200000
	STREAM_STATUS		= 0x800000

	MIXER_CHAN_ABSOLUTE	= 0x1000
	MIXER_CHAN_BUFFER	= 0x2000
	MIXER_CHAN_LIMIT	= 0x4000
	MIXER_CHAN_MATRIX	= 0x10000
	MIXER_CHAN_PAUSE	= 0x20000
	MIXER_CHAN_DOWNMIX	= 0x400000
	MIXER_CHAN_NORAMPIN	= 0x800000
	MIXER_BUFFER		= MIXER_CHAN_BUFFER
	MIXER_LIMIT			= MIXER_CHAN_LIMIT
	MIXER_MATRIX		= MIXER_CHAN_MATRIX
	MIXER_PAUSE			= MIXER_CHAN_PAUSE
	MIXER_DOWNMIX		= MIXER_CHAN_DOWNMIX
	MIXER_NORAMPIN		= MIXER_CHAN_NORAMPIN


class Bass:
	def __init__(self):
		if platform.system() == "Linux":
			self.base = cdll.LoadLibrary("lib/libbass.so")
			self.mix = cdll.LoadLibrary("lib/libbassmix.so")
		elif platform.system() == "Windows":
			self.base = cdll.LoadLibrary("lib/bass.dll")
			self.mix = cdll.LoadLibrary("lib/bassmix.dll")

	def ErrorGetCode(self):
		return self.base.BASS_ErrorGetCode()

	def Init(self, *args):
		self.base.BASS_Init(*args)

	def PluginLoad(self, *args):
		return self.base.BASS_PluginLoad(*args)

	def StreamCreateFile(self, *args):
		return self.base.BASS_StreamCreateFile(*args)

	def ChannelPlay(self, *args):
		self.base.BASS_ChannelPlay(*args)

	def ChannelGetData(self, *args):
		return self.base.BASS_ChannelGetData(*args)

	def Mixer_StreamCreate(self, *args):
		return self.mix.BASS_Mixer_StreamCreate(*args)

	def Mixer_StreamAddChannel(self, *args):
		self.mix.BASS_Mixer_StreamAddChannel(*args)