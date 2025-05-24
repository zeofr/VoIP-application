import time
import threading
import logging
from src.network import (
    VoIPServer, VoIPClient, SignalingServer, SignalingClient,
    SignalType, SignalingMessage, JitterBuffer, AudioEncryption
)
from src.audio import (
    AudioDevice, OpusCodec, AudioCapture, AudioPlayback,
    FrameHandler, AudioFrame
)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VoIPTest:
    def __init__(self):
        # Initialize components for client 1
        self.audio1 = AudioDevice()
        self.codec1 = OpusCodec()
        self.encryption1 = AudioEncryption()
        self.jitter_buffer1 = JitterBuffer()
        self.next_sequence1 = 0
        
        # Initialize components for client 2
        self.audio2 = AudioDevice()
        self.codec2 = OpusCodec()
        self.encryption2 = AudioEncryption()
        self.jitter_buffer2 = JitterBuffer()
        self.next_sequence2 = 0
        
        # Initialize network components
        self.signaling_server = SignalingServer(port=5000)
        self.voip_server = VoIPServer(port=5001)
        
        self.client1 = VoIPClient('localhost', 5001)
        self.client2 = VoIPClient('localhost', 5001)
        
        self.signaling_client1 = SignalingClient('localhost', 5000, 'client1')
        self.signaling_client2 = SignalingClient('localhost', 5000, 'client2')
        
        # Statistics
        self.frames_captured1 = 0
        self.frames_captured2 = 0
        self.frames_played1 = 0
        self.frames_played2 = 0
    
    def setup(self):
        """Set up the test environment"""
        # Start servers
        self.signaling_server.start()
        self.voip_server.start()
        
        # Connect clients
        self.signaling_client1.connect()
        self.signaling_client2.connect()
        
        # Start audio devices
        self.audio1.start_capture()
        self.audio1.start_playback()
        self.audio2.start_capture()
        self.audio2.start_playback()
        
        # Set up callbacks
        self._setup_callbacks()
        
        logger.info("Test environment set up complete")
    
    def _setup_callbacks(self):
        """Set up all necessary callbacks"""
        # Audio callbacks
        self.client1.set_audio_callback(self._handle_audio1)
        self.client2.set_audio_callback(self._handle_audio2)
        
        # Signaling callbacks
        self.signaling_client1.register_callback(SignalType.CALL, self._handle_call1)
        self.signaling_client2.register_callback(SignalType.CALL, self._handle_call2)
    
    def _handle_audio1(self, data):
        """Handle incoming audio for client 1"""
        try:
            # Decrypt
            decrypted = self.encryption1.decrypt(data['encrypted'], data['iv'])
            if not decrypted:
                logger.debug("Failed to decrypt audio for client 1")
                return
            
            # Decode
            decoded = self.codec1.decode(decrypted)
            if not decoded:
                logger.debug("Failed to decode audio for client 1")
                return
            
            # Add to jitter buffer
            self.jitter_buffer1.add_packet(data['sequence'], decoded)
            
            # Play audio
            while True:
                packet = self.jitter_buffer1.get_next_packet()
                if not packet:
                    break
                self.audio1.write_chunk(packet)
                self.frames_played1 += 1
                logger.debug(f"Client 1 played frame {self.frames_played1}")
        
        except Exception as e:
            logger.error(f"Error handling audio for client 1: {str(e)}")
    
    def _handle_audio2(self, data):
        """Handle incoming audio for client 2"""
        try:
            # Decrypt
            decrypted = self.encryption2.decrypt(data['encrypted'], data['iv'])
            if not decrypted:
                logger.debug("Failed to decrypt audio for client 2")
                return
            
            # Decode
            decoded = self.codec2.decode(decrypted)
            if not decoded:
                logger.debug("Failed to decode audio for client 2")
                return
            
            # Add to jitter buffer
            self.jitter_buffer2.add_packet(data['sequence'], decoded)
            
            # Play audio
            while True:
                packet = self.jitter_buffer2.get_next_packet()
                if not packet:
                    break
                self.audio2.write_chunk(packet)
                self.frames_played2 += 1
                logger.debug(f"Client 2 played frame {self.frames_played2}")
        
        except Exception as e:
            logger.error(f"Error handling audio for client 2: {str(e)}")
    
    def _handle_call1(self, message: SignalingMessage):
        """Handle call request for client 1"""
        if message.type == SignalType.CALL:
            # Accept call
            response = SignalingMessage(
                signal_type=SignalType.ACCEPT,
                sender='client1',
                recipient=message.sender
            )
            self.signaling_client1.send_message(response)
    
    def _handle_call2(self, message: SignalingMessage):
        """Handle call request for client 2"""
        if message.type == SignalType.CALL:
            # Accept call
            response = SignalingMessage(
                signal_type=SignalType.ACCEPT,
                sender='client2',
                recipient=message.sender
            )
            self.signaling_client2.send_message(response)
    
    def start_call(self):
        """Start a call between clients"""
        # Send call request
        message = SignalingMessage(
            signal_type=SignalType.CALL,
            sender='client1',
            recipient='client2'
        )
        self.signaling_client1.send_message(message)
        logger.info("Call request sent")
    
    def run(self):
        """Run the test"""
        try:
            # Set up environment
            self.setup()
            
            # Start call
            self.start_call()
            
            # Main loop
            while True:
                # Capture and send audio from client 1
                data = self.audio1.read_chunk()
                if data:
                    self.frames_captured1 += 1
                    logger.debug(f"Client 1 captured frame {self.frames_captured1}")
                    
                    # Encode
                    encoded = self.codec1.encode(data)
                    if encoded:
                        # Encrypt
                        encrypted, iv = self.encryption1.encrypt(encoded)
                        if encrypted:
                            # Send
                            self.client1.send_audio({
                                'encrypted': encrypted,
                                'iv': iv,
                                'sequence': self.next_sequence1
                            })
                            self.next_sequence1 += 1
                
                # Capture and send audio from client 2
                data = self.audio2.read_chunk()
                if data:
                    self.frames_captured2 += 1
                    logger.debug(f"Client 2 captured frame {self.frames_captured2}")
                    
                    # Encode
                    encoded = self.codec2.encode(data)
                    if encoded:
                        # Encrypt
                        encrypted, iv = self.encryption2.encrypt(encoded)
                        if encrypted:
                            # Send
                            self.client2.send_audio({
                                'encrypted': encrypted,
                                'iv': iv,
                                'sequence': self.next_sequence2
                            })
                            self.next_sequence2 += 1
                
                time.sleep(0.01)  # Small delay to prevent CPU overuse
        
        except KeyboardInterrupt:
            logger.info("Test stopped by user")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        # Stop audio devices
        self.audio1.cleanup()
        self.audio2.cleanup()
        
        # Stop clients
        self.client1.stop()
        self.client2.stop()
        self.signaling_client1.disconnect()
        self.signaling_client2.disconnect()
        
        # Stop servers
        self.voip_server.stop()
        self.signaling_server.stop()
        
        # Log statistics
        logger.info(f"Test statistics:")
        logger.info(f"Client 1: {self.frames_captured1} frames captured, {self.frames_played1} frames played")
        logger.info(f"Client 2: {self.frames_captured2} frames captured, {self.frames_played2} frames played")
        
        logger.info("Cleanup complete")

if __name__ == "__main__":
    test = VoIPTest()
    test.run() 