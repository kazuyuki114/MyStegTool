from ImageRGBManipulator import ImageRGBExtractor
from PIL import Image
import numpy as np

class ImageInImageSteganography:
    """
    ImageInImageSteganography class that encodes and decodes hidden image in the original image.
    """
    def __init__(self, bit_depth: int = 4, channel: int = 0):
        """
        :param channel: Channel to embed the secret image in (0 for red, 1 for green, 2 for blue).
        :param bit_depth: Number of LSBs on the cover to replace with MSBs of the secret (1-4 recommended).
        """
        self.channel = channel
        if not (1 <= bit_depth <= 4):
            raise ValueError("bit_depth must be between 1 and 4 for imperceptibility.")
        self.bit_depth = bit_depth


    def encode(self, original_img_path: str, secret_img_path: str, output_path : str) -> bool:
        """
        Hide a secret image in the original image.

        Args:
            original_img_path: Path to the input image
            secret_img_path: Text message to hide
            output_path: Path to save the steganographic image

        Returns:
            bool: True if encoding was successful, False otherwise
        """

        try:
            # Load the original image
            original_extractor = ImageRGBExtractor(original_img_path)
            original_extractor.load()

            # Load the secret image
            secret_extractor = ImageRGBExtractor(secret_img_path)
            secret_extractor.load()

            cover = original_extractor.arr
            secret = secret_extractor.arr

            if cover is None or secret is None:
                print("Error: Failed to load images")
                return False


            h, w, _ = cover.shape
            sh, sw, _ = secret.shape

            # Must fit header in first row: width * 3 channels >= 64 bits
            if w  < 64:
                print(f"Error: Cover width {w} too small to hold 64-bit header")
                return False

            # Compare height and width of original and secret image
            if sh > h or sw > w:
                print("Error: Secret image is larger than original image")
                return False

            # Prepare header bits
            header = format(sw, '032b') + format(sh, '032b')  # 64-char string
            print(f"Header: {header}")
            # Copy of the original image
            stego = original_extractor.arr.copy()
            # Create the clear mask
            mask_header = ""
            for i in range(8 - self.bit_depth - 1):
                mask_header += "1"

            for i in range(self.bit_depth + 1):
                mask_header += "0"
            print(f"Mask header: {mask_header}")
            clear_mask = int(mask_header, 2)
            # Embed header in the first row

            bit_idx = 0
            for x in range(w):
                if bit_idx < 64:
                    header_bit = (int(header[bit_idx]) & 1) << self.bit_depth
                    cover_bit = stego[0][x][self.channel] & clear_mask
                    stego[0, x, self.channel] = cover_bit | header_bit
                    bit_idx += 1
                else:
                    break
            # Img mask
            mask_img = ""
            for i in range(8 - self.bit_depth):
                mask_img += "1"

            for i in range(self.bit_depth):
                mask_img += "0"
            mask = int(mask_img, 2)
            print(f"Mask img: {mask_img}")

            for y in range(sh):
                for x in range(sw):
                    for c in range(3):
                        # Merge MSBs of secret image with LSBs of cover image
                        cover_part = stego[y][x][c] & mask
                        #print(f"Cover part: {bin(cover_part)}")
                        secret_part = secret[y][x][c] >> (8 - self.bit_depth)
                        #print(f"Secret part: {bin(secret_part)}")
                        stego[y][x][c] = cover_part | secret_part
            stego_img = Image.fromarray(stego, mode='RGB')
            stego_img.save(output_path, format='PNG')
            print(f"Message successfully hidden in {output_path}")
            return True
        except Exception as e:
            print(f"Error during encoding :{str(e)}")
            return False

    def decode(self, img_path: str, output_path: str) -> bool:
        """
        Extract the hidden secret image from a stego-image.

        Args:
            img_path: Path to the stego-image (PNG).
            output_path: Path to save the recovered secret image.

        Returns:
            True if decoding was successful, False otherwise.
        """
        try:
            # Load the original image
            img_extractor = ImageRGBExtractor(img_path)
            img_extractor.load()
            img = img_extractor.arr
            if img is None:
                print("Error: Failed to load image")
                return False
            stego_arr = img.copy()

            # 1) Read header
            # Build the clear-bit mask (only bit n is kept)
            mask_header = ""
            for i in range(8 - self.bit_depth - 1):
                mask_header += "0"
            mask_header += "1"
            for i in range(self.bit_depth):
                mask_header += "0"
            print(f"Mask header: {mask_header}")
            clear_mask = int(mask_header, 2)

            # Now extract 64 bits into a string
            header_bits = ""
            for i in range(64):
                bit = (stego_arr[0][i][self.channel] & clear_mask) >> self.bit_depth
                header_bits += str(bit)

            print(f"Extracted header bits: {header_bits}")
            # First 32 bits = width, next 32 bits = height
            sw = int(header_bits[:32], 2)
            sh = int(header_bits[32:], 2)

            print(f"Extracted secret width  : {sw}")
            print(f"Extracted secret height : {sh}")
            if sw == 0 or sh == 0 or sw > stego_arr.shape[1] or sh > stego_arr.shape[0]:
                print("Error: Invalid secret dimensions extracted")
                return False

            # 2) Extract pixel bits
            secret_arr = np.zeros((sh, sw, 3), dtype=np.uint8)

            # Img mask
            mask_img = ""
            for i in range(8 - self.bit_depth):
                mask_img += "0"

            for i in range(self.bit_depth):
                mask_img += "1"
            mask = int(mask_img, 2)
            print(f"Mask img: {mask_img}")

            for y in range(sh):
                for x in range(sw):
                    for c in range(3):
                        secret_arr[y, x, c] = (stego_arr[y][x][c] & mask) << (8 - self.bit_depth)

            # Save recovered secret
            recovered = Image.fromarray(secret_arr, mode='RGB')
            recovered.save(output_path, format='PNG')
            print(f"Secret image recovered successfully as {output_path}")
            return True

        except Exception as e:
            print(f"Error during decoding: {e}")
            return False
