import time
import threading
import queue
from typing import Optional, Tuple, Dict
import logging
from collections import OrderedDict

logger = logging.getLogger(__name__)

class JitterBuffer:
    def __init__(self, 
                 max_size: int = 50,  # Maximum number of packets to buffer
                 min_size: int = 10,  # Minimum number of packets before playback
                 max_delay: float = 0.5,  # Maximum delay in seconds
                 adaptive: bool = True):  # Whether to use adaptive buffering
        """
        Initialize jitter buffer
        
        Args:
            max_size: Maximum number of packets to buffer
            min_size: Minimum number of packets before playback
            max_delay: Maximum delay in seconds
            adaptive: Whether to use adaptive buffering
        """
        self.max_size = max_size
        self.min_size = min_size
        self.max_delay = max_delay
        self.adaptive = adaptive
        
        self.packet_queue: OrderedDict[int, bytes] = OrderedDict()
        self.next_sequence = 0
        self.last_sequence = -1
        self.last_playback_time = 0
        self.packet_times: Dict[int, float] = {}
        self.jitter = 0.0  # Current jitter estimate
        self.lock = threading.Lock()
        
        # Adaptive buffer parameters
        self.target_delay = 0.1  # Target delay in seconds
        self.current_delay = self.target_delay
        self.adaptation_rate = 0.1  # Rate of adaptation
    
    def add_packet(self, sequence: int, data: bytes) -> bool:
        """
        Add a packet to the buffer
        
        Args:
            sequence: Packet sequence number
            data: Packet data
        
        Returns:
            bool: True if packet was added successfully
        """
        with self.lock:
            # Check if packet is too old
            if self.last_sequence != -1 and sequence < self.last_sequence - self.max_size:
                logger.debug(f"Discarding old packet {sequence}")
                return False
            
            # Add packet to queue
            self.packet_queue[sequence] = data
            self.packet_times[sequence] = time.time()
            
            # Update last sequence
            if sequence > self.last_sequence:
                self.last_sequence = sequence
            
            # Calculate jitter
            if len(self.packet_times) > 1:
                self._update_jitter(sequence)
            
            # Trim buffer if too large
            while len(self.packet_queue) > self.max_size:
                self.packet_queue.popitem(last=False)
            
            return True
    
    def _update_jitter(self, sequence: int):
        """Update jitter estimate using RFC 3550 algorithm"""
        if sequence not in self.packet_times or sequence - 1 not in self.packet_times:
            return
        
        # Calculate inter-arrival time
        current_time = self.packet_times[sequence]
        prev_time = self.packet_times[sequence - 1]
        inter_arrival = current_time - prev_time
        
        # Update jitter estimate
        self.jitter += (abs(inter_arrival) - self.jitter) / 16.0
        
        # Update adaptive delay
        if self.adaptive:
            self._update_adaptive_delay()
    
    def _update_adaptive_delay(self):
        """Update adaptive delay based on jitter and packet loss"""
        # Increase delay if jitter is high
        if self.jitter > self.target_delay:
            self.current_delay = min(
                self.current_delay * (1 + self.adaptation_rate),
                self.max_delay
            )
        # Decrease delay if jitter is low
        else:
            self.current_delay = max(
                self.current_delay * (1 - self.adaptation_rate),
                self.target_delay
            )
    
    def get_next_packet(self) -> Optional[bytes]:
        """
        Get the next packet to play
        
        Returns:
            Optional[bytes]: Next packet data or None if not ready
        """
        with self.lock:
            current_time = time.time()
            
            # Check if we have enough packets
            if len(self.packet_queue) < self.min_size:
                return None
            
            # Check if enough time has passed since last playback
            if current_time - self.last_playback_time < self.current_delay:
                return None
            
            # Get next packet
            if self.next_sequence in self.packet_queue:
                data = self.packet_queue.pop(self.next_sequence)
                self.next_sequence += 1
                self.last_playback_time = current_time
                return data
            
            # Handle out-of-order packets
            if len(self.packet_queue) > 0:
                # Find the next available sequence
                next_seq = min(self.packet_queue.keys())
                if next_seq > self.next_sequence:
                    # We have a gap, update next_sequence
                    self.next_sequence = next_seq
                    data = self.packet_queue.pop(next_seq)
                    self.next_sequence += 1
                    self.last_playback_time = current_time
                    return data
            
            return None
    
    def get_stats(self) -> Dict:
        """Get buffer statistics"""
        with self.lock:
            return {
                'buffer_size': len(self.packet_queue),
                'jitter': self.jitter,
                'current_delay': self.current_delay,
                'next_sequence': self.next_sequence,
                'last_sequence': self.last_sequence
            }
    
    def reset(self):
        """Reset the buffer"""
        with self.lock:
            self.packet_queue.clear()
            self.packet_times.clear()
            self.next_sequence = 0
            self.last_sequence = -1
            self.last_playback_time = 0
            self.jitter = 0.0
            self.current_delay = self.target_delay 