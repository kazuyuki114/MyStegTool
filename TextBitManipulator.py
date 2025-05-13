from typing import List

class TextBitExtractor:
    def __init__(self, encoding: str = 'utf-8', delimiter: str = ''):
        """
        Initialize the TextBitExtractor with optional encoding and delimiter.

        :param encoding: The text encoding to use (default is 'utf-8').
        :param delimiter: A string to append to the text before conversion (default is an empty string).
        """
        self.encoding = encoding
        self.delimiter = delimiter

    @staticmethod
    def encode_text_to_bits(self, text : str) -> List[int]:
        """
        Convert the text to a flat list of bits (MSB first for each byte).
        :param text: The text to convert.
        :param self: The instance of the class.
        :return: List of 0s and 1s representing the text.
        """
        full_text = (text + self.delimiter).encode(self.encoding)
        bit_list = []
        for byte in full_text:
            for bit in range(7, -1, -1):
                bit_list.append((byte >> bit) & 1)
        return bit_list


class TextGenerator:
    @staticmethod
    def decode_bits_to_text(bits: List[int]) -> str:
        """
        Convert a list of bits (MSB-first) into a UTF-8 string.

        Args:
            bits: List of bits (0s and 1s)

        Returns:
            Decoded string
        """
        chars = []
        for i in range(0, len(bits), 8):
            byte = bits[i:i + 8]
            if len(byte) < 8:
                # Ignore incomplete byte at the end
                break
            byte_str = ''.join(str(bit) for bit in byte)
            byte_val = int(byte_str, 2)
            chars.append(chr(byte_val))
        return ''.join(chars)
