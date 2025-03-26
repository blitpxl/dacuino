#include <stdio.h>
#include <stdbool.h>
#include <fcntl.h>
#include <unistd.h>
#include <bass.h>
#include <bassmix.h>

#define BASSLOG(fmt) printf(fmt, BASS_ErrorGetCode()); fflush(stdout);
const char* path = "/home/blitpxl/Music/Men I Trust - Numb.flac";

int main()
{
	if (BASS_Init(0, -1, BASS_DEVICE_8BITS, NULL, NULL))
	{
		BASS_PluginLoad("bassflac", 0);
		DWORD stream = BASS_StreamCreateFile(false, path, 0, 0, 
			  BASS_SAMPLE_MONO | BASS_STREAM_DECODE | BASS_SAMPLE_8BITS);
		DWORD mixer = BASS_Mixer_StreamCreate(48000, 1, 
			  BASS_SAMPLE_MONO | BASS_STREAM_DECODE | BASS_SAMPLE_8BITS);
		BASS_Mixer_StreamAddChannel(mixer, stream, BASS_MIXER_CHAN_NORAMPIN);

		uint8_t samples[8300000];

		BASS_ChannelGetData(mixer, samples, sizeof(samples));

		for (int i = 0; i < sizeof(samples); i++)
		{
			if (samples[i] < 11)
				printf("%d\n", samples[i]);
			fflush(stdout);
		}

		int file = open("samples", O_CREAT|O_WRONLY, 0777);
		write(file, samples, sizeof(samples));
		close(file);
		printf("Decode process finished.\n");
	}
	else { BASSLOG("Failed to initialize BASS (%d)\n"); }
	return 0;
}