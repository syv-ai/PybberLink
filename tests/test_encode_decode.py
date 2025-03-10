import unittest
from pybberlink import encode_text_to_signal, decode_signal_to_text

class TestPybberlink(unittest.TestCase):
    def test_encode_decode(self):
        original_text = "Hello, Gibberlink!"
        # Encode the original text into an audio signal
        signal, pad_len, rs_encoded_length = encode_text_to_signal(original_text)
        # Decode the signal back into text
        decoded_text = decode_signal_to_text(signal, pad_bytes=pad_len, rs_encoded_length=rs_encoded_length)
        # Verify the decoded text matches the original
        self.assertEqual(decoded_text, original_text)

if __name__ == "__main__":
    unittest.main()