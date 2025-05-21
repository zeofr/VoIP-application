import time
from typing import Optional
import numpy as np
from collections import deque
from dataclasses import dataclass
import statistics

@dataclass
class AudioFrame:
    data: bytes
    timestamp: float
    sequence_number: int
    sample_rate: int
    channels: int
    frame_size: int
    is_silence: bool = False

class FrameHandler:
    def __init__(self, codec, frame_size=320):
        self.codec = codec
        self.frame_size = frame_size
        self.frame_duration = frame_size / codec.rate
        
        # Buffer management
        self.frame_buffer = deque(maxlen=10)
        self.jitter_buffer = deque(maxlen=5)
        self.current_jitter = 0.0
        self.buffer_underrun_count = 0
        self.buffer_overflow_count = 0
        
        # Statistics
        self.frame_count = 0
        self.total_bytes = 0
        self.start_time = time.time()
        self.silence_threshold = 100

    def create_frame(self, data: bytes) -> Optional[AudioFrame]:
        if not data:
            return None
            
        try:
            audio_data = np.frombuffer(data, dtype=np.int16)
            rms = np.sqrt(np.mean(audio_data.astype(np.float32)**2))
            is_silence = rms < self.silence_threshold
        except Exception:
            is_silence = False
            
        return AudioFrame(
            data=data,
            timestamp=time.time(),
            sequence_number=self.frame_count,
            sample_rate=self.codec.rate,
            channels=self.codec.channels,
            frame_size=self.frame_size,
            is_silence=is_silence
        )

    def add_frame(self, frame: AudioFrame) -> bool:
        if not self.validate_frame(frame):
            return False

        # Handle jitter
        if self.frame_buffer:
            last_frame = self.frame_buffer[-1]
            jitter = abs((frame.timestamp - last_frame.timestamp) - self.frame_duration)
            self.jitter_buffer.append(jitter)
            self.current_jitter = statistics.mean(self.jitter_buffer) if self.jitter_buffer else 0

        self.frame_buffer.append(frame)
        return True

    def get_next_frame(self) -> Optional[AudioFrame]:
        if not self.frame_buffer:
            return self._generate_silence_frame()
        return self.frame_buffer.popleft()

    def _generate_silence_frame(self) -> AudioFrame:
        silence_data = np.zeros(self.frame_size, dtype=np.int16).tobytes()
        return AudioFrame(
            data=silence_data,
            timestamp=time.time(),
            sequence_number=self.frame_count,
            sample_rate=self.codec.rate,
            channels=self.codec.channels,
            frame_size=self.frame_size,
            is_silence=True
        )

    def validate_frame(self, frame: AudioFrame) -> bool:
        return (
            len(frame.data) == self.frame_size * 2 and  # 16-bit samples
            frame.sample_rate == self.codec.rate and
            frame.channels == self.codec.channels
        )

    def get_statistics(self):
        return {
            'total_frames': self.frame_count,
            'buffer_level': len(self.frame_buffer),
            'current_jitter': self.current_jitter
        }