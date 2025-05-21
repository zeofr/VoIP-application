# src/audio/audio_device.py
import pyaudio
import numpy as np
from typing import Optional, Tuple, List
import wave
import time

class AudioDevice:
    def __init__(self, 
                 input_device_index: Optional[int] = None,
                 output_device_index: Optional[int] = None,
                 sample_rate: int = 16000,
                 channels: int = 1,
                 chunk_size: int = 320):
        """
        Initialize audio device for capture and playback
        
        Args:
            input_device_index: Index of input device (None for default)
            output_device_index: Index of output device (None for default)
            sample_rate: Audio sample rate in Hz
            channels: Number of audio channels
            chunk_size: Size of audio chunks in samples
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.format = pyaudio.paInt16
        
        # Initialize PyAudio
        self.p = pyaudio.PyAudio()
        
        # Get device info
        self.input_device_index = input_device_index
        self.output_device_index = output_device_index
        
        # Initialize streams
        self.input_stream = None
        self.output_stream = None
        
        # Buffer for playback
        self.playback_buffer = []
        self.is_playing = False
        
    def list_devices(self) -> List[Tuple[int, str, int, int]]:
        """List all available audio devices"""
        devices = []
        for i in range(self.p.get_device_count()):
            dev_info = self.p.get_device_info_by_index(i)
            devices.append((
                i,
                dev_info['name'],
                dev_info['maxInputChannels'],
                dev_info['maxOutputChannels']
            ))
        return devices
    
    def start_capture(self) -> bool:
        """Start audio capture"""
        try:
            self.input_stream = self.p.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=self.input_device_index,
                frames_per_buffer=self.chunk_size
            )
            return True
        except Exception as e:
            print(f"Error starting capture: {str(e)}")
            return False
    
    def start_playback(self) -> bool:
        """Start audio playback"""
        try:
            self.output_stream = self.p.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                output=True,
                output_device_index=self.output_device_index,
                frames_per_buffer=self.chunk_size
            )
            return True
        except Exception as e:
            print(f"Error starting playback: {str(e)}")
            return False
    
    def read_chunk(self) -> Optional[bytes]:
        """Read a chunk of audio data"""
        if not self.input_stream:
            return None
        try:
            return self.input_stream.read(self.chunk_size)
        except Exception as e:
            print(f"Error reading audio: {str(e)}")
            return None
    
    def write_chunk(self, data: bytes) -> bool:
        """Write a chunk of audio data"""
        if not self.output_stream:
            return False
        try:
            self.output_stream.write(data)
            return True
        except Exception as e:
            print(f"Error writing audio: {str(e)}")
            return False
    
    def stop_capture(self):
        """Stop audio capture"""
        if self.input_stream:
            self.input_stream.stop_stream()
            self.input_stream.close()
            self.input_stream = None
    
    def stop_playback(self):
        """Stop audio playback"""
        if self.output_stream:
            self.output_stream.stop_stream()
            self.output_stream.close()
            self.output_stream = None
    
    def cleanup(self):
        """Clean up resources"""
        self.stop_capture()
        self.stop_playback()
        self.p.terminate()
    
    def save_to_wav(self, data: bytes, filename: str):
        """Save audio data to WAV file"""
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)  # 16-bit audio
            wf.setframerate(self.sample_rate)
            wf.writeframes(data)
    
    def load_from_wav(self, filename: str) -> Optional[bytes]:
        """Load audio data from WAV file"""
        try:
            with wave.open(filename, 'rb') as wf:
                if wf.getnchannels() != self.channels:
                    print(f"Warning: WAV file has {wf.getnchannels()} channels, expected {self.channels}")
                if wf.getframerate() != self.sample_rate:
                    print(f"Warning: WAV file has {wf.getframerate()} Hz, expected {self.sample_rate}")
                return wf.readframes(wf.getnframes())
        except Exception as e:
            print(f"Error loading WAV file: {str(e)}")
            return None 