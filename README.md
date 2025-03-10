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
git clone https://github.com/yourusername/pybberlink.git
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

## License

[Add your chosen license here]

## Contributing

[Add contribution guidelines here]

## Authors

- Mads Henrichsen (mads@syv.ai)

## Acknowledgments

This project implements the Gibberlink protocol for audio-based data transmission. 