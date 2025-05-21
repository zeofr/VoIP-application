import sys
import time
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.audio.capture import AudioCapture
from src.audio.playback import AudioPlayback

def select_device(devices, device_type="input"):
    print(f"\nAvailable {device_type} devices:")
    for i, (index, name, channels, rates) in enumerate(devices):
        print(f"{i+1}. {name} (Channels: {channels}, Rates: {rates})")
    
    while True:
        try:
            choice = int(input(f"Select {device_type} device (1-{len(devices)}): ")) - 1
            if 0 <= choice < len(devices):
                selected = devices[choice]
                rate = selected[3][1] if 16000 in selected[3] else selected[3][0]
                return selected[0], rate
            print("Invalid selection")
        except ValueError:
            print("Enter a number")

def main():
    # Initialize with default values
    input_device = None
    output_device = None
    input_rate = 16000
    output_rate = 16000

    # Input device setup
    capture = AudioCapture()
    input_devices = capture.list_devices()
    if input_devices:
        input_device, input_rate = select_device(input_devices, "input")
    else:
        print("No input devices found!")
        return

    # Output device setup
    playback = AudioPlayback()
    output_devices = playback.list_devices()
    if output_devices:
        output_device, output_rate = select_device(output_devices, "output")
    else:
        print("No output devices found!")
        return

    # Reinitialize with selected devices
    capture = AudioCapture(
        device_index=input_device,
        rate=input_rate,
        channels=1
    )
    playback = AudioPlayback(
        device_index=output_device,
        rate=output_rate,
        channels=2 if output_rate >= 44100 else 1
    )

    # Start streams
    if not capture.start_stream():
        print("Failed to start input stream")
        return
    if not playback.start_stream():
        print("Failed to start output stream")
        return

    print("\nStreaming audio... (Press Ctrl+C to stop)")
    try:
        while True:
            frame = capture.read_frame()
            if frame:
                playback.play_frame(frame)
            time.sleep(0.001)
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        capture.stop_stream()
        playback.stop_stream()

if __name__ == "__main__":
    main()