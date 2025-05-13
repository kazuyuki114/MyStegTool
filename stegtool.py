#!/usr/bin/env python3
import sys
import argparse
from ImageSteganography import ImageSteganography
from ImageInImageSteganography import ImageInImageSteganography
from AudioSteganography import AudioSteganography

def main():
    parser = argparse.ArgumentParser(
        description="StegoTool: encode/decode text/images in images or text in audio"
    )
    parser.add_argument(
        "-m", "--mode",
        choices=["encode", "decode"], required=True,
        help="Mode: encode to hide data, decode to extract"
    )
    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "-i", "--image-text",
        nargs=3, metavar=("IMAGE", "MSG_OR_", "OUT"),
        help="Text↔Image. Encode: COVER IMAGE, MESSAGE, OUT_IMAGE. "
             "Decode: STEGO_IMAGE, _, OUT_TEXTFILE."
    )
    group.add_argument(
        "-I", "--image-image",
        nargs=3, metavar=("IMAGE", "SECRET_OR_", "OUT"),
        help="Image↔Image. Encode: COVER_IMAGE, SECRET_IMAGE, OUT_IMAGE. "
             "Decode: STEGO_IMAGE, _, OUT_IMAGE."
    )
    group.add_argument(
        "-a", "--audio-text",
        nargs=3, metavar=("WAV", "MSG_OR_", "OUT"),
        help="Text↔Audio. Encode: IN_WAV, MESSAGE, OUT_WAV. "
             "Decode: STEGO_WAV, _, OUT_TEXTFILE."
    )

    args = parser.parse_args()
    success = False

    if args.image_text:
        img_path, msg, out = args.image_text
        steg = ImageSteganography()
        if args.mode == "encode":
            success = steg.encode(img_path, msg, out)
        else:  # decode
            hidden = steg.decode(img_path)
            if hidden is not None:
                print(hidden)
                with open(out, "w", encoding="utf-8") as f:
                    f.write(hidden)
                success = True

    elif args.image_image:
        img_path, secret, out = args.image_image
        steg = ImageInImageSteganography()
        if args.mode == "encode":
            success = steg.encode(img_path, secret, out)
        else:
            # decode
            # secret arg is ignored; out is the recovered image path
            success = steg.decode(img_path, out)

    elif args.audio_text:
        wav_path, msg, out = args.audio_text
        steg = AudioSteganography()
        if args.mode == "encode":
            success = steg.encode(wav_path, msg, out)
        else:  # decode
            hidden = steg.decode(wav_path)
            if hidden is not None:
                print(hidden)
                with open(out, "w", encoding="utf-8") as f:
                    f.write(hidden)
                success = True

    else:
        parser.print_usage()
        sys.exit(1)

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
