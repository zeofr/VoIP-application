import socket
import threading
import queue
import time
from typing import Optional, Callable, Tuple, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UDPSocket:
    def __init__(self, 
                 local_port: int = 0,
                 remote_addr: Optional[Tuple[str, int]] = None,
                 buffer_size: int = 65535):
        """
        Initialize UDP socket wrapper
        
        Args:
            local_port: Local port to bind to (0 for random port)
            remote_addr: Remote address (host, port) for sending data
            buffer_size: Maximum packet size
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('0.0.0.0', local_port))
        self.remote_addr = remote_addr
        self.buffer_size = buffer_size
        self.is_running = False
        self.receive_thread: Optional[threading.Thread] = None
        self.packet_queue = queue.Queue()
        
        # Get actual bound port
        self.local_port = self.socket.getsockname()[1]
        logger.info(f"UDP socket bound to port {self.local_port}")
    
    def set_remote_addr(self, host: str, port: int):
        """Set remote address for sending data"""
        self.remote_addr = (host, port)
        logger.info(f"Remote address set to {host}:{port}")
    
    def start_receiving(self, callback: Optional[Callable[[bytes, Tuple[str, int]], None]] = None):
        """
        Start receiving packets in a separate thread
        
        Args:
            callback: Optional callback function(data, addr) to handle received packets
        """
        if self.is_running:
            return
        
        self.is_running = True
        self.receive_thread = threading.Thread(target=self._receive_loop, args=(callback,))
        self.receive_thread.daemon = True
        self.receive_thread.start()
        logger.info("Started receiving packets")
    
    def _receive_loop(self, callback: Optional[Callable[[bytes, Tuple[str, int]], None]]):
        """Internal receive loop"""
        while self.is_running:
            try:
                data, addr = self.socket.recvfrom(self.buffer_size)
                if callback:
                    callback(data, addr)
                else:
                    self.packet_queue.put((data, addr))
            except Exception as e:
                logger.error(f"Error receiving packet: {str(e)}")
                time.sleep(0.1)  # Prevent tight loop on error
    
    def send(self, data: bytes, addr: Optional[Tuple[str, int]] = None) -> bool:
        """
        Send data to specified address or default remote address
        
        Args:
            data: Data to send
            addr: Optional address to send to (overrides default remote_addr)
        
        Returns:
            bool: True if send was successful
        """
        try:
            target_addr = addr or self.remote_addr
            if not target_addr:
                logger.error("No remote address specified for sending")
                return False
            
            self.socket.sendto(data, target_addr)
            return True
        except Exception as e:
            logger.error(f"Error sending packet: {str(e)}")
            return False
    
    def receive(self, timeout: Optional[float] = None) -> Optional[Tuple[bytes, Tuple[str, int]]]:
        """
        Receive a packet from the queue
        
        Args:
            timeout: Optional timeout in seconds
        
        Returns:
            Tuple of (data, addr) or None if timeout
        """
        try:
            return self.packet_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def stop(self):
        """Stop receiving packets and cleanup"""
        self.is_running = False
        if self.receive_thread:
            self.receive_thread.join(timeout=1.0)
        self.socket.close()
        logger.info("UDP socket stopped and closed") 