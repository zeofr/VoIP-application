import sys
import os
import numpy as np
import wave
from pathlib import Path

# Add the src directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from src.audio.codec import AudioCodec

def test_opus_codec():
    """Test if Opus codec is working correctly"""
    print("Testing Opus codec functionality...")
    
    try:
        # Initialize the codec
        codec = AudioCodec()
        print("✓ Successfully initialized AudioCodec")
        
        # Create a test audio signal (1 second of 440 Hz sine wave)
        sample_rate = codec.rate
        duration = 1.0  # seconds
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        test_signal = np.sin(2 * np.pi * 440 * t) * 32767  # Scale to int16 range
        test_signal = test_signal.astype(np.int16)
        
        # Convert to bytes
        audio_data = test_signal.tobytes()
        print("✓ Generated test audio signal")
        
        # Split audio into frames
        frame_size = codec.frame_size
        num_frames = len(test_signal) // frame_size
        encoded_frames = []
        decoded_frames = []
        
        # Process each frame
        for i in range(num_frames):
            start = i * frame_size
            end = start + frame_size
            frame = test_signal[start:end]
            
            # Ensure frame is the correct size
            if len(frame) != frame_size:
                print(f"✗ Frame size mismatch: got {len(frame)}, expected {frame_size}")
                return False
            
            # Convert frame to bytes for encoding
            frame_bytes = frame.tobytes()
            
            # Encode frame
            try:
                # Pass frame size in samples to the encoder
                encoded_frame = codec.encoder.encode(frame_bytes, frame_size)
                if encoded_frame:
                    encoded_frames.append(encoded_frame)
                    # Decode frame
                    decoded_frame = codec.decoder.decode(encoded_frame, frame_size)
                    if decoded_frame:
                        decoded_frames.append(decoded_frame)
                    else:
                        print("✗ Failed to decode frame")
                        return False
                else:
                    print("✗ Failed to encode frame")
                    return False
            except Exception as e:
                print(f"✗ Error processing frame: {str(e)}")
                print(f"Frame size: {len(frame)} samples")
                print(f"Frame bytes size: {len(frame_bytes)} bytes")
                return False
        
        if not encoded_frames or not decoded_frames:
            print("✗ No frames were processed successfully")
            return False
            
        print("✓ Successfully encoded and decoded all frames")
        
        # Combine decoded frames
        decoded_data = b''.join(decoded_frames)
        
        # Save the original and decoded audio for comparison
        def save_wav(data, filename):
            with wave.open(str(filename), 'wb') as wf:  # Convert Path to string
                wf.setnchannels(codec.channels)
                wf.setsampwidth(2)  # 16-bit audio
                wf.setframerate(sample_rate)
                wf.writeframes(data)
        
        # Create output directory if it doesn't exist
        output_dir = Path(__file__).parent / "output"
        output_dir.mkdir(exist_ok=True)
        
        # Save both original and decoded audio
        save_wav(audio_data, output_dir / "original.wav")
        save_wav(decoded_data, output_dir / "decoded.wav")
        print("✓ Saved test audio files to examples/output/")
        
        # Basic quality check
        original = np.frombuffer(audio_data, dtype=np.int16)
        decoded = np.frombuffer(decoded_data, dtype=np.int16)
        
        # Ensure decoded audio is not empty
        if len(decoded) == 0:
            print("✗ Decoded audio is empty")
            return False
            
        # Check if decoded audio has reasonable length
        if abs(len(decoded) - len(original)) > len(original) * 0.1:  # Allow 10% difference
            print("✗ Decoded audio length differs significantly from original")
            return False
            
        print("\nOpus codec test completed successfully!")
        print("You can find the test audio files in examples/output/")
        print("Please listen to both files to verify audio quality.")
        return True
        
    except Exception as e:
        print(f"\n✗ Error during Opus codec test: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_opus_codec()
    sys.exit(0 if success else 1) 