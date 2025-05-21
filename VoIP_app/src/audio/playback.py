import pyaudio
from .frame_handler import FrameHandler, AudioFrame
from .codec import AudioCodec

class AudioPlayback:
    def __init__(self, device_index=None, rate=16000, channels=1):
        self.FRAME_SIZE = 320
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
            if dev['maxOutputChannels'] > 0:
                devices.append((
                    i,
                    dev['name'],
                    dev['maxOutputChannels'],
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
                    output=True,
                    output_device_index=self.device_index,
                    frames_per_buffer=self.FRAME_SIZE
                )
                return True
            except OSError as e:
                print(f"Audio output error: {e}")
        return False

    def play_frame(self, frame: AudioFrame) -> bool:
        try:
            if frame and self.stream:
                self.stream.write(frame.data)
                return True
            return False
        except Exception as e:
            print(f"Playback error: {e}")
            return False

    def stop_stream(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()