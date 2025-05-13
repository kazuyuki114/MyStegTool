from PIL import Image
import numpy as np
from typing import Union

class ImageRGBExtractor:
    def __init__(self, path: str):
        """
        Initialize with the path to the image.
        """
        self.path = path
        self.arr: Union[np.ndarray, None] = None

    def load(self) -> None:
        """
        Load the image and convert to an RGB NumPy array.
        """
        img = Image.open(self.path).convert('RGB')
        self.arr = np.array(img, dtype=np.uint8)



