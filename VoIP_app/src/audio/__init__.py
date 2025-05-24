"""
Audio processing module for VoIP application
"""

from .audio_device import AudioDevice
from .codec import OpusCodec
from .capture import AudioCapture
from .playback import AudioPlayback
from .frame_handler import FrameHandler, AudioFrame

__all__ = [
    'AudioDevice',
    'OpusCodec',
    'AudioCapture',
    'AudioPlayback',
    'FrameHandler',
    'AudioFrame'
] 