import opuslib
import numpy as np

class AudioCodec:
    def __init__(self, rate=16000, channels=1, application=opuslib.APPLICATION_AUDIO):
        self.rate = rate
        self.channels = channels
        self.frame_size = 320  # 20ms frames at 16kHz

        # Initialize encoder and decoder
        self.encoder = opuslib.Encoder(rate, channels, application)
        self.decoder = opuslib.Decoder(rate, channels)

    def encode(self, pcm_data):
        """Encode PCM data to Opus format"""
        if isinstance(pcm_data, bytes):
            pcm = np.frombuffer(pcm_data, dtype=np.int16)
        else:
            pcm = pcm_data
        return self.encoder.encode(pcm, self.frame_size)

    def decode(self, encoded_data):
        """Decode Opus data to PCM format"""
        decoded = self.decoder.decode(encoded_data, self.frame_size)
        return np.array(decoded, dtype=np.int16).tobytes()