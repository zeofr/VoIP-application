# VoIP Application

A Python-based Voice over IP (VoIP) application that implements real-time audio communication with features like audio compression, encryption, and network jitter handling.

## Features

- Real-time audio capture and playback
- Opus codec for high-quality audio compression
- AES-256 encryption for secure communication
- Adaptive jitter buffer for network latency handling
- TCP-based signaling for call setup/teardown
- UDP-based audio streaming
- Client-server architecture

## Project Structure

```
VoIP_app/
├── src/
│   ├── audio/
│   │   ├── __init__.py
│   │   ├── audio_device.py    # Audio capture/playback
│   │   ├── codec.py          # Opus codec implementation
│   │   ├── capture.py        # Audio capture utilities
│   │   ├── playback.py       # Audio playback utilities
│   │   └── frame_handler.py  # Audio frame processing
│   │
│   ├── network/
│   │   ├── __init__.py
│   │   ├── udp_socket.py     # UDP socket wrapper
│   │   ├── server.py         # VoIP server implementation
│   │   ├── client.py         # VoIP client implementation
│   │   ├── jitter_buffer.py  # Network jitter handling
│   │   ├── crypto.py         # Audio encryption
│   │   └── signaling.py      # Call signaling protocol
│   │
│   └── __init__.py
│
├── test_voip.py              # Test implementation
├── requirements.txt          # Project dependencies
└── README.md                 # This file
```

## Dependencies

- Python 3.7+
- PyAudio (audio capture/playback)
- Opuslib (audio compression)
- PyCryptodome (encryption)
- NumPy (audio processing)

## Installation

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   .venv\Scripts\activate     # Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the Test Implementation

The test implementation demonstrates a VoIP call between two clients on the same machine:

```bash
python test_voip.py
```

This will:
1. Start a signaling server (port 5000)
2. Start a VoIP server (port 5001)
3. Create two clients and connect them
4. Start a call between the clients
5. Handle audio capture, compression, encryption, and playback

### Using the Components

#### Audio Device

```python
from src.audio import AudioDevice

# Initialize audio device
audio = AudioDevice()

# Start capture and playback
audio.start_capture()
audio.start_playback()

# Read audio data
data = audio.read_chunk()

# Write audio data
audio.write_chunk(data)

# Cleanup
audio.cleanup()
```

#### Opus Codec

```python
from src.audio import OpusCodec

# Initialize codec
codec = OpusCodec(sample_rate=16000, channels=1)

# Encode audio
encoded = codec.encode(pcm_data)

# Decode audio
decoded = codec.decode(encoded)
```

#### Jitter Buffer

```python
from src.network import JitterBuffer

# Initialize buffer
buffer = JitterBuffer()

# Add packet
buffer.add_packet(sequence, data)

# Get next packet
packet = buffer.get_next_packet()
```

#### Encryption

```python
from src.network import AudioEncryption

# Initialize encryption
crypto = AudioEncryption()

# Encrypt data
encrypted, iv = crypto.encrypt(data)

# Decrypt data
decrypted = crypto.decrypt(encrypted, iv)
```

#### Signaling

```python
from src.network import SignalingServer, SignalingClient

# Start server
server = SignalingServer(port=5000)
server.start()

# Connect client
client = SignalingClient('localhost', 5000, 'client1')
client.connect()

# Send message
client.send_message(message)
```

## Implementation Details

### Audio Processing

- Sample rate: 16 kHz
- Channels: 1 (mono)
- Frame size: 320 samples (20ms at 16kHz)
- Bit depth: 16-bit PCM

### Network Protocol

- Signaling: TCP (port 5000)
- Audio: UDP (port 5001)
- Packet size: 320 bytes (20ms of audio)

### Security

- AES-256 encryption
- Unique IV per packet
- PBKDF2 key derivation
- Secure key exchange during call setup

### Jitter Buffer

- Adaptive buffer sizing
- RFC 3550 jitter estimation
- Packet reordering
- Configurable delay

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 