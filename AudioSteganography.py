import wave
import numpy as np

from TextBitManipulator import TextBitExtractor, TextGenerator


class AudioSteganography:
    """
    AudioSteganography class that encodes and decodes messages in audio using LSB steganography.
    """

    def __init__(self, delimiter: str = "<END>"):
        """
        Initialize the steganography tool with a custom delimiter.

        Args:
            delimiter: String delimiter to mark the end of the hidden message
        """
        self.delimiter = delimiter
    def encode(self, audio_path: str, message: str, output_path: str) -> bool:
        """
        Hide a message in an audio using LSB steganography.

        Args:
            audio_path: Path to the input WAV file
            message: Text message to hide
            output_path: Path to save the steganographic audio (.wav)

        Returns:
            bool: True if encoding was successful, False otherwise
        """
        try:
            # Load the audio
            wav = wave.open(audio_path, 'rb')
            params = wav.getparams()
            frames = wav.readframes(params.nframes)
            samples = np.frombuffer(frames, dtype=np.int16)
            wav.close()

            print(f"Sample size: {samples.size}")

            # Convert the hidden message to bits
            text_extractor = TextBitExtractor(delimiter=self.delimiter)
            message_bits = text_extractor.encode_text_to_bits(text_extractor, message)

            # Check the message + length > max capacity of the image
            if len(message_bits) + 32 > samples.size:
                print(
                    f"Error: Message too large for image. Needs {len(message_bits)} bits, audio has {samples.size} bits.")
                return False

            # Encode message length first (32 bits) for length
            msg_len = len(message_bits)
            len_bits = format(msg_len, '032b')
            print(f"Encoding message length: {msg_len}")

            stego = samples.copy()
            # Encode length
            for i in range(32):
                # Clear LSB and set it to the current bit of the length
                stego[i] = (stego[i] & 0xFE) | int(len_bits[i])

            for i in range(len(message_bits)):
                if i + 32 < stego.size:
                    # Clear LSB and set it to the current bit of the length
                    stego[i + 32] = (stego[i + 32] & 0xFE) | message_bits[i]

            out = wave.open(output_path, 'wb')
            out.setparams(params)
            out.writeframes(stego.tobytes())
            out.close()

            return True
        except Exception as e:
            print(f"Error during encoding :{str(e)}")
            return False


    def decode(self, audio_path: str) -> str | None:
        """
        Extract a hidden message from a steganographic audio.

        Args:
            audio_path: Path to the steganographic audio

        Returns:
            str : Extracted message or None if extraction failed
        """
        try:
            # Load the audio
            wav = wave.open(audio_path, 'rb')
            params = wav.getparams()
            frames = wav.readframes(params.nframes)
            samples = np.frombuffer(frames, dtype=np.int16)
            wav.close()

            len_bits = ""
            for i in range(32):
                len_bits += str(samples[i] & 1)

            print(f"Extracted length bits: {len_bits}")
            msg_len = int(len_bits, 2)
            print(f"Decoding message length: {msg_len}")

            # Validate message length
            if msg_len <= 0 or msg_len > samples.size - 32:
                print("Error: Invalid message length detected. Audio may not contain hidden data.")
                return None

            # Extract message bits
            extracted_bits = []
            for i in range(msg_len):
                if i + 32 < samples.size:
                    extracted_bits.append(samples[i + 32] & 1)

            # Convert bits to text
            decoded_text = TextGenerator.decode_bits_to_text(extracted_bits)

            # Remove delimiter
            if self.delimiter in decoded_text:
                decoded_text = decoded_text.split(self.delimiter)[0]
                return decoded_text
            else:
                print("Warning: Delimiter not found. Message might be incomplete or corrupted.")
                return decoded_text

        except Exception as e:
            print(f"Error during decoding :{str(e)}")
            return None
