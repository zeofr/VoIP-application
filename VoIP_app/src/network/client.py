import threading
import time
from typing import Optional, Tuple, Callable
import logging
import json
import base64
from .udp_socket import UDPSocket

logger = logging.getLogger(__name__)

class VoIPClient:
    def __init__(self, server_host: str, server_port: int):
        """
        Initialize VoIP client
        
        Args:
            server_host: Server hostname/IP
            server_port: Server port
        """
        self.socket = UDPSocket()
        self.server_addr = (server_host, server_port)
        self.is_running = False
        self.client_thread: Optional[threading.Thread] = None
        self.on_audio_received: Optional[Callable[[bytes], None]] = None
        self.packets_sent = 0
        self.packets_received = 0
    
    def start(self):
        """Start the client"""
        if self.is_running:
            return
        
        self.is_running = True
        self.client_thread = threading.Thread(target=self._client_loop)
        self.client_thread.daemon = True
        self.client_thread.start()
        logger.info(f"VoIP client started, connected to server at {self.server_addr[0]}:{self.server_addr[1]}")
    
    def _client_loop(self):
        """Main client loop"""
        self.socket.start_receiving(self._handle_packet)
        
        while self.is_running:
            time.sleep(0.1)  # Prevent tight loop
    
    def _handle_packet(self, data: bytes, addr: Tuple[str, int]):
        """
        Handle incoming packets
        
        Args:
            data: Received packet data
            addr: Source address (host, port)
        """
        try:
            # Decode JSON data
            json_data = json.loads(data.decode())
            
            # Convert base64 strings back to bytes
            audio_data = {
                'encrypted': base64.b64decode(json_data['encrypted']),
                'iv': base64.b64decode(json_data['iv']),
                'sequence': json_data['sequence']
            }
            
            self.packets_received += 1
            logger.debug(f"Received packet {self.packets_received} from {addr}, size: {len(data)} bytes")
            
            if self.on_audio_received:
                self.on_audio_received(audio_data)
        except Exception as e:
            logger.error(f"Error handling packet: {str(e)}")
    
    def send_audio(self, audio_data: dict) -> bool:
        """
        Send audio data to the server
        
        Args:
            audio_data: Dictionary containing audio data and metadata
                {
                    'encrypted': bytes,  # Encrypted audio data
                    'iv': bytes,        # Initialization vector
                    'sequence': int     # Sequence number
                }
        
        Returns:
            bool: True if send was successful
        """
        try:
            # Convert bytes to base64 strings
            json_data = {
                'encrypted': base64.b64encode(audio_data['encrypted']).decode(),
                'iv': base64.b64encode(audio_data['iv']).decode(),
                'sequence': audio_data['sequence']
            }
            
            # Convert to JSON and send
            data = json.dumps(json_data).encode()
            success = self.socket.send(data, self.server_addr)
            
            if success:
                self.packets_sent += 1
                logger.debug(f"Sent packet {self.packets_sent}, size: {len(data)} bytes")
            
            return success
        except Exception as e:
            logger.error(f"Error sending audio: {str(e)}")
            return False
    
    def set_audio_callback(self, callback: Callable[[bytes], None]):
        """
        Set callback for received audio data
        
        Args:
            callback: Function to call with received audio data
        """
        self.on_audio_received = callback
    
    def stop(self):
        """Stop the client and cleanup"""
        self.is_running = False
        if self.client_thread:
            self.client_thread.join(timeout=1.0)
        self.socket.stop()
        logger.info(f"VoIP client stopped. Packets sent: {self.packets_sent}, received: {self.packets_received}") 