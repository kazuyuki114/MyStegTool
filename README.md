## Overview

This repository provides a unified command‐line steganography tool that supports three modes:

- **Text ↔ Image**: hide or extract text messages in PNG images  
- **Image ↔ Image**: hide or extract a secret image within a cover image  
- **Text ↔ Audio**: hide or extract text messages in lossless WAV audio

Under the hood, all methods use LSB (Least Significant Bit) substitution to embed data in the least‐significant bits of pixels or audio samples. A small header encodes metadata (e.g. secret image dimensions or message length) so decoding always reconstructs the exact hidden content.

## Features

- **Multi‐mode support** via a single executable (`stegtool.py`), with `-m encode|decode` and `-i`, `-I`, `-a` flags  
- **Flexible bit-depth** for image→image mode (1–4 LSBs) and channel selection (R/G/B)  
- **Header metadata** ensures robust decoding of message lengths or secret image dimensions  
- **Lossless formats**: PNG for images, WAV (PCM) for audio—avoiding compression artifacts  
- **Simple CLI** with clear usage and exit codes (`0` = success, `1` = failure)

## Installation

1. Clone this repository and `cd` into it:
   ```bash
   git clone https://github.com/yourusername/stegtool.git
   cd stegtool
   ```
2. Ensure you have Python 3.8+ and install dependencies:
    ```bash
   pip install -r requirements.txt
   ```
3. Make the main script executable:
    ```bash
    chmod +x stegtool.py   
    ```
**Note**: The tool expects these modules in the same directory (or installed):
- ImageTextSteganography.py
- ImageInImageSteganography.py
- AudioSteganography.py
- ImageRGBManipulator.py 

## Command-Line Usage
Run with -h to see full help:
    ```bash
    ./stegtool.py -h
    ```
## Modes and Flags
- -m, --mode: encode or decode
- -i, --image-text: text - image mode (nargs=3)
- -I, --image-image: image - image mode (nargs=3)
- -a, --audio-text: text - audio mode (nargs=3)

### Text In Image
```bash
# Encode: hide “Hello” in cover.png → stego.png
./stegtool.py -m encode -i cover.png "Hello" stego.png

# Decode: extract from stego.png → hidden.txt
./stegtool.py -m decode -i stego.png "" hidden.txt
```
### Image In Image
```bash
# Encode: hide secret.png in cover.png → stego.png
./stegtool.py -m encode -I cover.png secret.png stego.png

# Decode: extract secret from stego.png → recovered.png
./stegtool.py -m decode -I stego.png "" recovered.png
```
### Text Int Audio
```bash
# Encode: hide “Secret” in song.wav → stego.wav
./stegtool.py -m encode -a song.wav "Secret" stego.wav

# Decode: extract text from stego.wav → message.txt
./stegtool.py -m decode -a stego.wav "" message.txt
```

## How It Works
1. Text - Image (ImageSteganography)

    Convert text + delimiter into a bit stream.

    Optionally prefix a 32-bit message length header.

    Flatten the image’s RGB bytes, then overwrite each byte’s LSB with one bit.

    Reshape and save as PNG to preserve LSBs.

2. Image - Image (ImageInImageSteganography)

    Resize secret image to fit the cover dimensions (or record its size in a header).

    For each cover pixel channel, clear the lowest n bits, then insert the top n bits of the secret pixel channel.

    Save as PNG to avoid color‐loss artifacts.

3. Text - Audio (AudioSteganography)

    Encode text into bits (with delimiter).

    Prefix a 32-bit length header.

    Read 16-bit PCM samples from a WAV, then replace each sample’s LSB with one bit of data.

    Write out a new WAV with identical audio parameters.

## Internals & Customization
- Bit‐depth (-n or constructor arg): Change how many LSBs you use in image - image mode (default bit depth = 4). Fewer bits → less capacity but better invisibility.
- Channel Selection (-c or constructor arg): Choose R/G/B for header embedding in image - image mode.
- Delimiter: The default (END) marks message boundaries for text modes. You can adjust it in your code.

## License
This project is licensed under the MIT License. Feel free to adapt and extend!
