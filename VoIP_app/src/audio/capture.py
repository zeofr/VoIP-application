from typing import Optional
import pyaudio
from .frame_handler import FrameHandler, AudioFrame
from .codec import AudioCodec

class AudioCapture:
    def __init__(self, device_index=None, rate=16000, channels=1):
        self.CHUNK = 320
        self.RATE = rate
        self.CHANNELS = channels
        self.FORMAT = pyaudio.paInt16
        self.device_index = device_index
        
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.codec = AudioCodec(rate=rate, channels=channels)
        self.frame_handler = FrameHandler(codec=self.codec)

    def list_devices(self):
        devices = []
        for i in range(self.p.get_device_count()):
            dev = self.p.get_device_info_by_index(i)
            if dev['maxInputChannels'] > 0:
                devices.append((
                    i,
                    dev['name'],
                    dev['maxInputChannels'],
                    [8000, 16000, 44100, 48000]  # Supported rates
                ))
        return devices

    def start_stream(self, retries=3):
        for _ in range(retries):
            try:
                self.stream = self.p.open(
                    format=self.FORMAT,
                    channels=self.CHANNELS,
                    rate=self.RATE,
                    input=True,
                    input_device_index=self.device_index,
                    frames_per_buffer=self.CHUNK
                )
                return True
            except OSError as e:
                print(f"Audio input error: {e}")
        return False

    def read_frame(self) -> Optional[AudioFrame]:
        try:
            data = self.stream.read(self.CHUNK, exception_on_overflow=False)
            return self.frame_handler.create_frame(data)
        except Exception as e:
            print(f"Capture error: {e}")
            return None

    def stop_stream(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()