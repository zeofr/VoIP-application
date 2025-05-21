import time
import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.audio.capture import AudioCapture
from src.audio.playback import AudioPlayback

def print_progress_bar(progress, length=50):
    """Print a progress bar"""
    filled = int(length * progress)
    bar = '█' * filled + '░' * (length - filled)
    sys.stdout.write(f'\rBuffer: [{bar}] {progress:.1%}')
    sys.stdout.flush()

def main():
    # Initialize audio components with larger buffer
    capture = AudioCapture(chunk_size=320, channels=1, rate=16000)
    playback = AudioPlayback(chunk_size=320, channels=1, rate=16000)
    
    print("🎙️  Starting audio test... Press Ctrl+C to stop")
    print("Monitoring audio chunks and frame handling...")
    print("Buffer size: 10 frames")
    
    try:
        # Start streams
        capture.start_stream()
        playback.start_stream()
        
        # Fill initial buffer
        print("\nFilling initial buffer...")
        for _ in range(5):  # Fill half the buffer
            frame = capture.read_frame()
            if frame:
                playback.frame_handler.add_frame(frame)
                time.sleep(0.02)  # 20ms delay
        
        print("Buffer filled, starting playback...")
        
        while True:
            # Read a new frame
            frame = capture.read_frame()
            
            if frame:
                # Get audio level
                audio_level = capture.get_audio_level(frame.data)
                
                # Get frame statistics
                stats = capture.get_frame_statistics()
                
                # Clear line and print stats
                sys.stdout.write('\r' + ' ' * 80 + '\r')  # Clear line
                print(f"\nFrame #{frame.sequence_number}")
                print(f"Timestamp: {frame.timestamp:.3f}")
                print(f"Audio Level: {audio_level:.2f}")
                print(f"Buffer Level: {stats['buffer_level']:.1%}")
                print(f"Frames Processed: {stats['frames_processed']}")
                print(f"Frames Dropped: {stats['frames_dropped']}")
                
                # Print buffer visualization
                print_progress_bar(stats['buffer_level'])
                
                # Add frame to buffer
                playback.frame_handler.add_frame(frame)
                
                # Try to play a frame from buffer
                next_frame = playback.frame_handler.get_next_frame()
                if next_frame:
                    playback.stream.write(next_frame.data, playback.CHUNK)
            
            # Small delay to prevent CPU overload
            time.sleep(0.01)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping audio test...")
    finally:
        # Cleanup
        capture.stop_stream()
        playback.stop_stream()
        print("✅ Test completed")

if __name__ == "__main__":
    main() 