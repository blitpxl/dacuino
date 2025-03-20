#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <bass.h>
#include <bassmix.h>

#define BASSLOG(fmt) printf(fmt, BASS_ErrorGetCode()); fflush(stdout);
const char* path = "/home/blitpxl/Music/1_Alvvays-Pharmacist (1).wav";

int main()
{
	if (BASS_Init(-1, 44000, BASS_DEVICE_MONO | BASS_DEVICE_8BITS, NULL, NULL))
	{
		BASS_PluginLoad("bassflac", 0);
		DWORD stream = BASS_StreamCreateFile(false, path, 0, 0, BASS_STREAM_DECODE | BASS_SAMPLE_MONO | BASS_SAMPLE_8BITS);
		DWORD mixer = BASS_Mixer_StreamCreate(16000, 1, BASS_STREAM_DECODE | BASS_SAMPLE_MONO | BASS_SAMPLE_8BITS);

		BASS_Mixer_StreamAddChannel(mixer, stream, BASS_MIXER_CHAN_NORAMPIN);

		uint8_t samples[8200000];
		BASS_ChannelGetData(mixer, samples, sizeof(samples));

		int file = open("samples", O_CREAT|O_WRONLY, 0777);
		write(file, samples, sizeof(samples));
		close(file);
	}
	else { BASSLOG("Failed to initialize BASS (%d)\n"); }
	return 0;
}