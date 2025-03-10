# Pybberlink

Pybberlink is a Python package that implements the Gibberlink protocol for encoding and decoding text messages into audio signals. It provides a robust way to transmit text data through sound waves using frequency-based encoding with Reed-Solomon error correction.

## Features

- Text to audio signal encoding
- Audio signal to text decoding
- Support for both audible and ultrasonic frequency modes
- Reed-Solomon error correction for reliable data transmission
- Configurable protocol parameters
- Parallel tone channels for efficient data transmission

## Installation

You can install Pybberlink using pip:

```bash
pip install pybberlink
```

Or install from source:

```bash
git clone https://github.com/syv-ai/pybberlink.git
cd pybberlink
pip install -e .
```

## Requirements

- Python 3.6 or higher
- NumPy
- reedsolo

## Usage

### Basic Example

```python
from pybberlink import encode_text_to_signal, decode_signal_to_text

# Encode text to audio signal
text = "Hello, Gibberlink!"
signal, pad_len, rs_encoded_length = encode_text_to_signal(text)

# Decode audio signal back to text
decoded_text = decode_signal_to_text(signal, pad_bytes=pad_len, rs_encoded_length=rs_encoded_length)
print(decoded_text)  # Output: Hello, Gibberlink!
```

### Advanced Usage

#### Ultrasonic Mode

```python
# Encode in ultrasonic mode
signal, pad_len, rs_encoded_length = encode_text_to_signal(
    text,
    ultrasonic=True
)
```

#### Custom Parameters

```python
# Customize encoding parameters
signal, pad_len, rs_encoded_length = encode_text_to_signal(
    text,
    sample_rate=44100,      # Custom sample rate
    symbol_duration=2048,    # Longer symbol duration
    rs_ecc_bytes=8          # More error correction bytes
)
```

### Complete Example with WAV File I/O

This example demonstrates how to encode text to an audio signal, save it to a WAV file, read it back, and decode it:

```python
import wave
import numpy as np
from pybberlink import encode_text_to_signal, decode_signal_to_text

def save_to_wav(filename, signal, sample_rate=48000):
    """
    Save a NumPy array signal to a WAV file.
    
    Parameters:
        filename (str): Path to the output WAV file.
        signal (np.ndarray): 1-D NumPy array containing the audio signal (float values).
        sample_rate (int): The sample rate used for the signal.
    """
    # Normalize signal to the range [-1, 1] if necessary
    max_val = np.max(np.abs(signal))
    if max_val > 0:
        normalized_signal = signal / max_val
    else:
        normalized_signal = signal

    # Convert the normalized float signal to 16-bit PCM format
    int_signal = np.int16(normalized_signal * 32767)

    # Write the data to a WAV file using the wave module
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)          # Mono audio
        wf.setsampwidth(2)          # 16-bit samples = 2 bytes
        wf.setframerate(sample_rate)
        wf.writeframes(int_signal.tobytes())

def read_from_wav(filename):
    """
    Read a WAV file and return the audio signal as a NumPy array along with its sample rate.
    
    Parameters:
        filename (str): Path to the WAV file.
    
    Returns:
        tuple: (signal (np.ndarray), sample_rate (int))
    """
    with wave.open(filename, 'rb') as wf:
        sample_rate = wf.getframerate()
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        n_frames = wf.getnframes()
        frames = wf.readframes(n_frames)
        
        # Assuming mono audio and 16-bit PCM format
        signal = np.frombuffer(frames, dtype=np.int16).astype(np.float32)
        # Convert back to float range [-1, 1]
        signal = signal / 32767.0
    
    return signal, sample_rate

# Example usage:
if __name__ == '__main__':
    text = """Hello world,
    This is a test of the Gibberlink protocol.
    It should be able to encode and decode text into an audio signal.
    """
    # Encode text into an audio signal
    signal, pad_len, rs_length = encode_text_to_signal(text)
    
    # Save the signal to a WAV file
    wav_filename = "output.wav"
    save_to_wav(wav_filename, signal)
    
    # Later, read the signal back from the WAV file
    loaded_signal, sr = read_from_wav(wav_filename)
    
    # Decode the loaded signal back into text
    decoded_text = decode_signal_to_text(loaded_signal, pad_bytes=pad_len, rs_encoded_length=rs_length)
    print("Decoded text:", decoded_text)

## Technical Details

### Protocol Parameters

- Normal mode base frequency: 1875 Hz
- Ultrasonic mode base frequency: 15000 Hz
- Frequency step: 46.875 Hz
- Tones per nibble: 16 (4-bit encoding)
- Parallel tone channels: 6 (24 bits per symbol)
- Default sample rate: 48000 Hz
- Default symbol duration: 1024 samples
- Default Reed-Solomon ECC bytes: 4

### Encoding Process

1. Text is converted to UTF-8 bytes
2. Reed-Solomon error correction is applied
3. Data is padded to ensure complete symbols
4. Bytes are split into 4-bit nibbles
5. Nibbles are encoded using frequency-shift keying (FSK)
6. Multiple tones are combined into a single audio signal

### Decoding Process

1. Signal is split into symbols
2. Hann window is applied to reduce spectral leakage
3. FFT is computed for each symbol
4. Frequency peaks are detected to recover nibbles
5. Nibbles are combined into bytes
6. Reed-Solomon error correction is applied
7. Bytes are decoded back to UTF-8 text

## Testing

The package includes unit tests to verify encoding and decoding functionality. Run tests using:

```bash
python -m unittest tests/test_encode_decode.py
```

## Acknowledgments

This project implements the Gibberlink protocol for audio-based data transmission. 