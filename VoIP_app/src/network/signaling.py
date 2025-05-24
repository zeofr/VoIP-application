import json
import socket
import threading
import queue
from typing import Optional, Dict, Callable, Tuple
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class SignalType(Enum):
    REGISTER = "register"
    CALL = "call"
    ACCEPT = "accept"
    REJECT = "reject"
    HANGUP = "hangup"
    ICE_CANDIDATE = "ice_candidate"
    ERROR = "error"

class SignalingMessage:
    def __init__(self, 
                 signal_type: SignalType,
                 sender: str,
                 recipient: Optional[str] = None,
                 data: Optional[Dict] = None):
        self.type = signal_type
        self.sender = sender
        self.recipient = recipient
        self.data = data or {}
    
    def to_json(self) -> str:
        """Convert message to JSON string"""
        return json.dumps({
            'type': self.type.value,
            'sender': self.sender,
            'recipient': self.recipient,
            'data': self.data
        })
    
    @classmethod
    def from_json(cls, json_str: str) -> 'SignalingMessage':
        """Create message from JSON string"""
        data = json.loads(json_str)
        return cls(
            signal_type=SignalType(data['type']),
            sender=data['sender'],
            recipient=data.get('recipient'),
            data=data.get('data', {})
        )

class SignalingServer:
    def __init__(self, host: str = '0.0.0.0', port: int = 0):
        """
        Initialize signaling server
        
        Args:
            host: Host to bind to
            port: Port to bind to (0 for random port)
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.socket.listen(5)
        self.port = self.socket.getsockname()[1]
        
        self.clients: Dict[str, socket.socket] = {}
        self.callbacks: Dict[SignalType, Callable] = {}
        self.is_running = False
        self.server_thread: Optional[threading.Thread] = None
        
        logger.info(f"Signaling server initialized on port {self.port}")
    
    def start(self):
        """Start the signaling server"""
        if self.is_running:
            return
        
        self.is_running = True
        self.server_thread = threading.Thread(target=self._server_loop)
        self.server_thread.daemon = True
        self.server_thread.start()
        logger.info("Signaling server started")
    
    def _server_loop(self):
        """Main server loop"""
        while self.is_running:
            try:
                client_socket, addr = self.socket.accept()
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, addr)
                )
                client_thread.daemon = True
                client_thread.start()
            except Exception as e:
                logger.error(f"Error accepting connection: {str(e)}")
    
    def _handle_client(self, client_socket: socket.socket, addr: Tuple[str, int]):
        """Handle client connection"""
        client_id = None
        try:
            # Wait for registration
            data = client_socket.recv(1024)
            if not data:
                return
            
            message = SignalingMessage.from_json(data.decode())
            if message.type != SignalType.REGISTER:
                return
            
            # Register client
            client_id = message.sender
            self.clients[client_id] = client_socket
            logger.info(f"Client registered: {client_id}")
            
            # Handle client messages
            while self.is_running:
                data = client_socket.recv(1024)
                if not data:
                    break
                
                message = SignalingMessage.from_json(data.decode())
                self._handle_message(message)
        
        except Exception as e:
            logger.error(f"Error handling client: {str(e)}")
        finally:
            if client_id and client_id in self.clients:
                del self.clients[client_id]
            client_socket.close()
            if client_id:
                logger.info(f"Client disconnected: {client_id}")
    
    def _handle_message(self, message: SignalingMessage):
        """Handle signaling message"""
        # Call callback if registered
        if message.type in self.callbacks:
            self.callbacks[message.type](message)
        
        # Forward message to recipient
        if message.recipient and message.recipient in self.clients:
            try:
                self.clients[message.recipient].send(message.to_json().encode())
            except Exception as e:
                logger.error(f"Error forwarding message: {str(e)}")
    
    def register_callback(self, signal_type: SignalType, callback: Callable):
        """Register callback for signal type"""
        self.callbacks[signal_type] = callback
    
    def stop(self):
        """Stop the signaling server"""
        self.is_running = False
        for client in self.clients.values():
            client.close()
        self.socket.close()
        logger.info("Signaling server stopped")

class SignalingClient:
    def __init__(self, server_host: str, server_port: int, client_id: str):
        """
        Initialize signaling client
        
        Args:
            server_host: Signaling server host
            server_port: Signaling server port
            client_id: Unique client identifier
        """
        self.server_host = server_host
        self.server_port = server_port
        self.client_id = client_id
        self.socket: Optional[socket.socket] = None
        self.callbacks: Dict[SignalType, Callable] = {}
        self.is_running = False
        self.client_thread: Optional[threading.Thread] = None
    
    def connect(self) -> bool:
        """Connect to signaling server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_host, self.server_port))
            
            # Send registration
            message = SignalingMessage(
                signal_type=SignalType.REGISTER,
                sender=self.client_id
            )
            self.socket.send(message.to_json().encode())
            
            # Start receive thread
            self.is_running = True
            self.client_thread = threading.Thread(target=self._receive_loop)
            self.client_thread.daemon = True
            self.client_thread.start()
            
            logger.info(f"Connected to signaling server as {self.client_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error connecting to server: {str(e)}")
            return False
    
    def _receive_loop(self):
        """Receive loop for incoming messages"""
        while self.is_running:
            try:
                data = self.socket.recv(1024)
                if not data:
                    break
                
                message = SignalingMessage.from_json(data.decode())
                if message.type in self.callbacks:
                    self.callbacks[message.type](message)
            
            except Exception as e:
                logger.error(f"Error receiving message: {str(e)}")
                break
        
        self.is_running = False
    
    def send_message(self, message: SignalingMessage) -> bool:
        """Send signaling message"""
        try:
            if not self.socket:
                return False
            self.socket.send(message.to_json().encode())
            return True
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return False
    
    def register_callback(self, signal_type: SignalType, callback: Callable):
        """Register callback for signal type"""
        self.callbacks[signal_type] = callback
    
    def disconnect(self):
        """Disconnect from signaling server"""
        self.is_running = False
        if self.socket:
            self.socket.close()
        logger.info("Disconnected from signaling server") 