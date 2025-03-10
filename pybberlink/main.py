import numpy as np
import reedsolo

# Protocol parameters (easily configurable)
F0_normal = 1875.0    # Base frequency for audible mode [Hz]
F0_ultra  = 15000.0   # Base frequency for ultrasonic mode [Hz]
dF = 46.875           # Frequency step between adjacent tones [Hz]
tones_per_nibble = 16 # 16 possible values for a 4-bit nibble (0-15)
parallel_tones   = 6  # Six channels per symbol (24 bits per symbol)

# Audio and RS parameters (configurable)
sample_rate = 48000         # Samples per second for audio
symbol_duration = 1024      # Samples per symbol (affects frequency resolution)
rs_ecc_bytes = 4            # Number of error correction bytes for Reed-Solomon

def get_freq_table(ultrasonic=False):
    """
    Precompute a lookup table of frequencies for each of the six bands and for each nibble value.
    """
    base_freq = F0_ultra if ultrasonic else F0_normal
    table = np.zeros((parallel_tones, tones_per_nibble))
    for band in range(parallel_tones):
        for nibble in range(tones_per_nibble):
            table[band, nibble] = base_freq + (band * tones_per_nibble + nibble) * dF
    return table

def get_bin_table(freq_table):
    """
    Convert the frequency lookup table into corresponding FFT bin indices.
    """
    bin_table = np.round(freq_table * symbol_duration / sample_rate).astype(int)
    return bin_table

def encode_text_to_signal(text, ultrasonic=False, sample_rate=48000, symbol_duration=1024, rs_ecc_bytes=4):
    """
    Encode a text string into an audio signal using the Gibberlink protocol.
    
    This function applies Reed-Solomon error correction to the data,
    precomputes a frequency lookup table, and uses vectorized sine generation
    to create the audio signal.
    
    Returns:
        full_signal: A NumPy array containing the concatenated audio waveform.
        pad_len: Number of padding bytes added.
        rs_encoded_length: The length of the RS-encoded data.
    """
    # Convert text to bytes
    data = text.encode('utf-8')
    # Encode with Reed-Solomon error correction
    rs = reedsolo.RSCodec(rs_ecc_bytes)
    data_with_ecc = rs.encode(data)
    
    # Pad the data so its length is a multiple of 3 (since 3 bytes per symbol)
    pad_len = (3 - (len(data_with_ecc) % 3)) % 3
    if pad_len:
        data_with_ecc += b'\x00' * pad_len

    # Precompute the frequency lookup table for the selected mode
    freq_table = get_freq_table(ultrasonic)
    
    # Time axis for one symbol (vectorized sine generation)
    t = np.linspace(0, symbol_duration / sample_rate, num=symbol_duration, endpoint=False)
    signal_chunks = []
    
    # Process data 3 bytes (24 bits) at a time
    for i in range(0, len(data_with_ecc), 3):
        chunk = data_with_ecc[i:i+3]
        b1, b2, b3 = chunk
        # Convert three bytes into six 4-bit nibbles
        nibbles = np.array([
            (b1 >> 4) & 0xF, b1 & 0xF,
            (b2 >> 4) & 0xF, b2 & 0xF,
            (b3 >> 4) & 0xF, b3 & 0xF
        ])
        # Lookup the frequency for each band and its corresponding nibble
        freqs = np.array([freq_table[band, nibbles[band]] for band in range(parallel_tones)])
        # Generate sine waves for all six frequencies simultaneously and sum them
        sine_waves = np.sin(2 * np.pi * freqs[:, None] * t)
        symbol_wave = np.sum(sine_waves, axis=0)
        signal_chunks.append(symbol_wave)
    
    full_signal = np.concatenate(signal_chunks)
    return full_signal, pad_len, len(data_with_ecc)

def decode_signal_to_text(signal, pad_bytes=0, rs_encoded_length=None, ultrasonic=False, sample_rate=48000, symbol_duration=1024, rs_ecc_bytes=4):
    """
    Decode an audio signal back into text using the pybberlink protocol.
    
    This function reshapes the signal into symbols, applies a Hann window to each symbol
    to reduce spectral leakage, computes FFTs in batch, and uses precomputed FFT bin indices
    to detect the transmitted nibbles. Finally, it applies Reed-Solomon error correction to
    recover the original message.
    """
    n_symbols = len(signal) // symbol_duration
    symbols = signal[:n_symbols * symbol_duration].reshape(n_symbols, symbol_duration)
    
    # Apply a Hann window for better FFT resolution
    window = np.hanning(symbol_duration)
    windowed = symbols * window
    
    # Batch FFT computation along the time axis
    spectra = np.fft.rfft(windowed, axis=1)
    magnitudes = np.abs(spectra)
    
    # Precompute lookup tables for frequencies and their FFT bin indices
    freq_table = get_freq_table(ultrasonic)
    bin_table = get_bin_table(freq_table)  # shape: (6, 16)
    
    # Prepare an array to hold the detected nibbles for each symbol (each symbol has 6 nibbles)
    nibble_matrix = np.zeros((n_symbols, parallel_tones), dtype=int)
    
    # For each band (channel), determine the transmitted nibble by comparing magnitudes at candidate bins
    for band in range(parallel_tones):
        candidate_mags = np.zeros((n_symbols, tones_per_nibble))
        for nibble in range(tones_per_nibble):
            bin_index = bin_table[band, nibble]
            # Check if bin_index is within the FFT result range
            if bin_index < magnitudes.shape[1]:
                candidate_mags[:, nibble] = magnitudes[:, bin_index]
            else:
                candidate_mags[:, nibble] = 0.0
        nibble_matrix[:, band] = np.argmax(candidate_mags, axis=1)
    
    # Reconstruct bytes: every 6 nibbles form 3 bytes
    reconstructed = bytearray()
    for row in nibble_matrix:
        byte1 = (row[0] << 4) | row[1]
        byte2 = (row[2] << 4) | row[3]
        byte3 = (row[4] << 4) | row[5]
        reconstructed.extend([byte1, byte2, byte3])
    
    # Remove padding bytes (if any)
    if pad_bytes:
        reconstructed = reconstructed[:-pad_bytes]
    
    # If an RS encoded length is provided, truncate the bytearray accordingly
    if rs_encoded_length is not None and len(reconstructed) > rs_encoded_length:
        reconstructed = reconstructed[:rs_encoded_length]
    
    # Decode using Reed-Solomon error correction; note that rs.decode returns a tuple
    rs = reedsolo.RSCodec(rs_ecc_bytes)
    try:
        decoded_data = rs.decode(bytes(reconstructed))[0]
    except reedsolo.ReedSolomonError as e:
        print("Reed-Solomon decoding error:", e)
        decoded_data = bytes(reconstructed)
    
    return decoded_data.decode('utf-8', errors='ignore')