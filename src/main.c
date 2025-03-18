#include <bass.h>
#include <stdio.h>

#define DATA_LENGTH 4096*4

int main()
{
	BASS_Init(0, 8000, BASS_DEVICE_MONO | BASS_DEVICE_8BITS, NULL, NULL);
	BASS_PluginLoad("bassflac", 0);

	unsigned char buffer[DATA_LENGTH];
	unsigned int stream = BASS_StreamCreateFile(false, "/home/blitpxl/Documents/sample.wav", 0, 0, BASS_STREAM_DECODE | BASS_SAMPLE_MONO | BASS_SAMPLE_8BITS);
	BASS_ChannelGetData(stream, buffer, sizeof(buffer));

	for (int i = 0; i < DATA_LENGTH; i++)
	{
		printf("%d,", buffer[i]);
	}

	scanf("%s");
}