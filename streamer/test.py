from bass import Bass, Flags

bass = Bass()
bass.Init(-1, 48000, 0, 0, 0, 0)
s = bass.StreamCreateFile(0, "/home/blitpxl/Downloads/youtube_T5UhLx59yDs_audio.mp3".encode(), 0, 0, 0)
print(bass.ErrorGetCode())