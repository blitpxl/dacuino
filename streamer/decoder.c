#include <stdio.h>
#include <stdbool.h>
#include <fcntl.h>
#include <unistd.h>
#include <bass.h>
#include <bassmix.h>

#define BASSLOG(fmt) printf(fmt, BASS_ErrorGetCode()); fflush(stdout);
const char* path = "/home/blitpxl/Downloads/EliminateHQ - This Song Is Copyright Free.wav";

int main()
{
	if (BASS_Init(-1, -1, BASS_DEVICE_MONO | BASS_DEVICE_8BITS, NULL, NULL))
	{
		BASS_PluginLoad("bassflac", 0);
		DWORD stream = BASS_StreamCreateFile(false, path, 0, 0, 
			BASS_STREAM_DECODE | BASS_SAMPLE_MONO | BASS_SAMPLE_8BITS);
		DWORD mixer = BASS_Mixer_StreamCreate(48000, 1, 
			BASS_STREAM_DECODE | BASS_SAMPLE_MONO | BASS_SAMPLE_8BITS);
		BASS_Mixer_StreamAddChannel(mixer, stream, BASS_MIXER_CHAN_NORAMPIN);

		QWORD stream_length = BASS_ChannelGetLength(mixer, BASS_POS_BYTE);
		unsigned int sample_count =  (int)(BASS_ChannelBytes2Seconds(mixer, stream_length) * 44100);

		uint8_t samples[8300000];
		BASS_ChannelGetData(mixer, samples, sizeof(samples));

		int file = open("samples", O_CREAT|O_WRONLY, 0777);
		write(file, samples, sizeof(samples));
		close(file);
		printf("Decode process finished.\n");
	}
	else { BASSLOG("Failed to initialize BASS (%d)\n"); }
	return 0;
}