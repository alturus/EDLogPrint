import argparse
import os

import filetype
from PIL import Image


def verify_image_file(filename):
    try:
        im = Image.open(filename)
        im.verify()
        im.close()
        im = Image.open(filename)
        im.transpose(Image.FLIP_LEFT_RIGHT)
        im.close()
    except Exception:
        return False

    return True


def convert_to_png(filename):
    folder = os.path.dirname(filename)

    out_filename = filename.split('.')[0] + '.png'
    out_filename = os.path.join(folder, out_filename)

    try:
        with Image.open(filename) as im:
            im.save(out_filename)
    except OSError:
        print('Unable to convert the image file')
        return False

    if verify_image_file(out_filename):
        os.remove(filename)
    else:
        os.remove(out_filename)
        return False

    return out_filename


def is_valid_image_file(parser, filename):
    """Simple check the filename is an image file"""

    if not os.path.isfile(filename):
        parser.error(f'The file {filename} does not exist!')
    if not filetype.image(filename):
        parser.error(f'The file {filename} not an image file!')
    return filename


def parse_arguments():
    parser = argparse.ArgumentParser(description='Convert image to .png')
    parser.add_argument('filename',
                        help='input image file name',
                        type=lambda x: is_valid_image_file(parser, x))
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    convert_to_png(args.filename)
