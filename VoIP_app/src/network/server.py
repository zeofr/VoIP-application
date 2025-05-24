import threading
import time
from typing import Dict, Set, Optional, Tuple
import logging
from .udp_socket import UDPSocket

logger = logging.getLogger(__name__)

class VoIPServer:
    def __init__(self, port: int = 0):
        """
        Initialize VoIP server
        
        Args:
            port: Port to listen on (0 for random port)
        """
        self.socket = UDPSocket(local_port=port)
        self.clients: Dict[Tuple[str, int], Set[Tuple[str, int]]] = {}  # client -> set of peers
        self.is_running = False
        self.server_thread: Optional[threading.Thread] = None
    
    def start(self):
        """Start the server"""
        if self.is_running:
            return
        
        self.is_running = True
        self.server_thread = threading.Thread(target=self._server_loop)
        self.server_thread.daemon = True
        self.server_thread.start()
        logger.info(f"VoIP server started on port {self.socket.local_port}")
    
    def _server_loop(self):
        """Main server loop"""
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
        # Add client if new
        if addr not in self.clients:
            self.clients[addr] = set()
            logger.info(f"New client connected: {addr[0]}:{addr[1]}")
        
        # Route packet to all peers
        for client_addr, peers in self.clients.items():
            if client_addr != addr:  # Don't send back to sender
                self.socket.send(data, client_addr)
    
    def add_peer(self, client_addr: Tuple[str, int], peer_addr: Tuple[str, int]):
        """
        Add a peer connection for a client
        
        Args:
            client_addr: Client address
            peer_addr: Peer address to connect to
        """
        if client_addr not in self.clients:
            self.clients[client_addr] = set()
        self.clients[client_addr].add(peer_addr)
        logger.info(f"Added peer {peer_addr[0]}:{peer_addr[1]} for client {client_addr[0]}:{client_addr[1]}")
    
    def remove_peer(self, client_addr: Tuple[str, int], peer_addr: Tuple[str, int]):
        """
        Remove a peer connection for a client
        
        Args:
            client_addr: Client address
            peer_addr: Peer address to remove
        """
        if client_addr in self.clients:
            self.clients[client_addr].discard(peer_addr)
            logger.info(f"Removed peer {peer_addr[0]}:{peer_addr[1]} for client {client_addr[0]}:{client_addr[1]}")
    
    def remove_client(self, client_addr: Tuple[str, int]):
        """
        Remove a client and all its peer connections
        
        Args:
            client_addr: Client address to remove
        """
        if client_addr in self.clients:
            del self.clients[client_addr]
            logger.info(f"Removed client {client_addr[0]}:{client_addr[1]}")
    
    def stop(self):
        """Stop the server and cleanup"""
        self.is_running = False
        if self.server_thread:
            self.server_thread.join(timeout=1.0)
        self.socket.stop()
        logger.info("VoIP server stopped") 