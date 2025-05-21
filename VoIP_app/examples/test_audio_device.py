import sys
import time
from pathlib import Path

# Add the src directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from src.audio.audio_device import AudioDevice

def test_audio_device():
    """Test audio device capture and playback"""
    print("Testing audio device functionality...")
    
    try:
        # Initialize audio device
        device = AudioDevice()
        print("✓ Successfully initialized AudioDevice")
        
        # List available devices
        devices = device.list_devices()
        print("\nAvailable audio devices:")
        for idx, name, in_channels, out_channels in devices:
            print(f"Device {idx}: {name}")
            print(f"  Input channels: {in_channels}")
            print(f"  Output channels: {out_channels}")
        
        # Start capture
        if not device.start_capture():
            print("✗ Failed to start audio capture")
            return False
        print("✓ Started audio capture")
        
        # Start playback
        if not device.start_playback():
            print("✗ Failed to start audio playback")
            return False
        print("✓ Started audio playback")
        
        # Record and play for 5 seconds
        print("\nRecording and playing audio for 5 seconds...")
        print("Please speak into your microphone")
        
        start_time = time.time()
        while time.time() - start_time < 5:
            # Read audio chunk
            chunk = device.read_chunk()
            if chunk:
                # Play the chunk
                device.write_chunk(chunk)
        
        print("✓ Completed audio test")
        
        # Clean up
        device.cleanup()
        print("✓ Cleaned up audio resources")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error during audio device test: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_audio_device()
    sys.exit(0 if success else 1) 