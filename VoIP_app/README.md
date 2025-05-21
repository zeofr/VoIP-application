# VoIP Application

A Python-based Voice over IP (VoIP) application that provides audio capture, encoding/decoding, and playback capabilities.

## Features

- Audio capture and playback using PyAudio
- Opus codec support for high-quality audio compression
- Modular architecture for easy extension

## Project Structure

```
VoIP_app/
├── src/                    # Source code
│   ├── audio/             # Audio handling modules
│   ├── network/           # Network communication
│   └── utils/             # Utility functions
├── tests/                 # Test files
├── examples/              # Example applications
└── requirements.txt       # Python dependencies
```

## Setup

1. Install the Opus library:
   - Windows: Download from https://opus-codec.org/downloads/
   - Linux: `sudo apt-get install libopus-dev`
   - macOS: `brew install opus`

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   .venv\Scripts\activate     # Windows
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the simple client example:
```bash
python examples/simple_client.py
```

## Development

- `src/audio/capture.py`: Audio capture functionality
- `src/audio/playback.py`: Audio playback functionality
- `src/audio/codec.py`: Opus codec handling

## Requirements

- Python 3.7+
- PyAudio
- opuslib
- numpy 