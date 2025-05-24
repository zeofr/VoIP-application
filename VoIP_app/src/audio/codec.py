import opuslib
import numpy as np
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class OpusCodec:
    def __init__(self,
                 sample_rate: int = 16000,
                 channels: int = 1,
                 frame_size: int = 320,  # 20ms at 16kHz
                 bitrate: int = 16000):  # 16 kbps
        """
        Initialize Opus codec
        
        Args:
            sample_rate: Audio sample rate in Hz
            channels: Number of audio channels
            frame_size: Frame size in samples
            bitrate: Target bitrate in bits per second
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.frame_size = frame_size
        self.bitrate = bitrate
        
        # Initialize encoder
        self.encoder = opuslib.Encoder(
            sample_rate,
            channels,
            opuslib.APPLICATION_VOIP
        )
        self.encoder.bitrate = bitrate
        
        # Initialize decoder
        self.decoder = opuslib.Decoder(
            sample_rate,
            channels
        )
        
        logger.info(f"Initialized Opus codec: {sample_rate}Hz, {channels}ch, {bitrate}bps")
    
    def encode(self, pcm_data: bytes) -> Optional[bytes]:
        """
        Encode PCM audio data to Opus
        
        Args:
            pcm_data: Raw PCM audio data
        
        Returns:
            Optional[bytes]: Encoded Opus data or None if encoding failed
        """
        try:
            # Ensure data length is correct
            if len(pcm_data) != self.frame_size * 2:  # 2 bytes per sample
                logger.warning(f"Invalid PCM data length: {len(pcm_data)}")
                return None
            
            # Encode to Opus
            encoded = self.encoder.encode(pcm_data, self.frame_size)
            return encoded
        except Exception as e:
            logger.error(f"Error encoding audio: {str(e)}")
            return None
    
    def decode(self, opus_data: bytes) -> Optional[bytes]:
        """
        Decode Opus data to PCM
        
        Args:
            opus_data: Encoded Opus data
        
        Returns:
            Optional[bytes]: Decoded PCM data or None if decoding failed
        """
        try:
            # Decode from Opus
            decoded = self.decoder.decode(opus_data, self.frame_size)
            return decoded
        except Exception as e:
            logger.error(f"Error decoding audio: {str(e)}")
            return None
    
    def set_bitrate(self, bitrate: int):
        """
        Set encoder bitrate
        
        Args:
            bitrate: Target bitrate in bits per second
        """
        try:
            self.encoder.bitrate = bitrate
            self.bitrate = bitrate
            logger.info(f"Set bitrate to {bitrate}bps")
        except Exception as e:
            logger.error(f"Error setting bitrate: {str(e)}")
    
    def get_stats(self) -> dict:
        """Get codec statistics"""
        return {
            'sample_rate': self.sample_rate,
            'channels': self.channels,
            'frame_size': self.frame_size,
            'bitrate': self.bitrate
        }