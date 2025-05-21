# import pyaudio
# import opuslib

# CHUNK = 320  # ~20ms at 16kHz mono
# FORMAT = pyaudio.paInt16
# CHANNELS = 1
# RATE = 16000

# p = pyaudio.PyAudio()

# stream = p.open(format=FORMAT,
#                 channels=CHANNELS,
#                 rate=RATE,
#                 input=True,
#                 output=True,
#                 frames_per_buffer=CHUNK)

# print("🎙️  Looping audio... Press Ctrl+C to stop.")
# try:
#     while True:
#         data = stream.read(CHUNK)
#         stream.write(data, CHUNK)
# except KeyboardInterrupt:
#     print("\n🛑 Stopping loop.")
#     stream.stop_stream()
#     stream.close()
#     p.terminate()

# encoder = opuslib.Encoder(RATE, CHANNELS, opuslib.APPLICATION_AUDIO)
# decoder = opuslib.Decoder(RATE, CHANNELS)

# while True:
#     raw = stream.read(CHUNK)
#     compressed = encoder.encode(raw, CHUNK)
#     decompressed = decoder.decode(compressed, CHUNK)
#     stream.write(decompressed)


import opuslib

encoder = opuslib.Encoder(48000, 2, opuslib.APPLICATION_AUDIO)
decoder = opuslib.Decoder(48000, 2)

# Raw PCM bytes (dummy example)
pcm_data = b'\x00\x00' * 960  # 20ms of silence at 48kHz stereo

# Encode
encoded = encoder.encode(pcm_data, frame_size=960)

# Decode
decoded = decoder.decode(encoded, frame_size=960)

print(f"Encoded length: {len(encoded)}")
print(f"Decoded length: {len(decoded)}")
