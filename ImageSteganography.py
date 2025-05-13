from PIL import Image
from ImageRGBManipulator import ImageRGBExtractor
from TextBitManipulator import TextBitExtractor, TextGenerator


class ImageSteganography:
    """
    ImageSteganography class that encodes and decodes messages in images using LSB steganography.
    """
    def __init__(self, delimiter: str = "<END>"):
        """
        Initialize the steganography tool with a custom delimiter.

        Args:
            delimiter: String delimiter to mark the end of the hidden message
        """
        self.delimiter = delimiter

    def encode(self, image_path: str, message: str, output_path: str) -> bool:
        """
        Hide a message in an image using LSB steganography.

        Args:
            image_path: Path to the input image
            message: Text message to hide
            output_path: Path to save the steganographic image

        Returns:
            bool: True if encoding was successful, False otherwise
        """
        try:
            # Load the image
            img_extractor = ImageRGBExtractor(image_path)
            img_extractor.load()

            if img_extractor.arr is None:
                print("Error: Failed to load image")
                return False

            # Convert the hidden message to bits
            text_extractor = TextBitExtractor(delimiter=self.delimiter)
            message_bits = text_extractor.encode_text_to_bits(text_extractor, message)

            # Check if the given image is large enough
            img_array = img_extractor.arr
            max_capacity = img_array.size

            # Check the message + length > max capacity of the image
            if len(message_bits) + 32 > max_capacity:
                print(
                    f"Error: Message too large for image. Needs {len(message_bits)} bits, image has {max_capacity} bits.")
                return False

            # Encode message length first (32 bits) for length
            msg_len = len(message_bits)
            len_bits = format(msg_len, '032b')
            print(f"Encoding message length: {msg_len}")

            # Flatten the array for easy handling
            stego_array = img_array.copy()
            flat_stego = stego_array.flatten()

            # Encode length
            for i in range(32):
                # Clear LSB and set it to the current bit of the length
                flat_stego[i] = (flat_stego[i] & 0xFE) | int(len_bits[i])

            # Encode message bits
            for i in range(len(message_bits)):
                if i + 32 < flat_stego.size:
                    # Clear LSB and set it to the current message bit
                    flat_stego[i + 32] = (flat_stego[i + 32] & 0xFE) | message_bits[i]

            # Reshape back to original dimensions
            stego_array = flat_stego.reshape(img_array.shape)

            # Save the steganographic image
            stego_img = Image.fromarray(stego_array, mode='RGB')
            stego_img.save(output_path, format='PNG') # save png for reserving the rgb format

            print(f"Message successfully hidden in {output_path}")
            return True

        except Exception as e:
            print(f"Error during encoding: {str(e)}")
            return False

    def decode(self, img_path: str) -> str | None:
        """
        Extract a hidden message from a steganographic image.

        Args:
            img_path: Path to the steganographic image

        Returns:
            str : Extracted message or None if extraction failed
        """
        try:
            # Load the steganographic image
            img_extractor = ImageRGBExtractor(img_path)
            img_extractor.load()

            if img_extractor.arr is None:
                print("Error: Failed to load steganographic image")
                return None
            # Flatten the array
            flat_img = img_extractor.arr.flatten()

            # Extract the length (first 32 bits)
            len_bits = ""
            for i in range(32):
                len_bits += str(flat_img[i] & 1)
            print(f"Extracted length bits: {len_bits}")
            msg_len = int(len_bits, 2)
            print(f"Decoding message length: {msg_len}")
            # Validate message length
            if msg_len <= 0 or msg_len > flat_img.size - 32:
                print("Error: Invalid message length detected. Image may not contain hidden data.")
                return None

            # Extract message bits
            extracted_bits = []
            for i in range(msg_len):
                if i + 32 < flat_img.size:
                    extracted_bits.append(flat_img[i + 32] & 1)

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
            print(f"Error during decoding: {str(e)}")
            return None
