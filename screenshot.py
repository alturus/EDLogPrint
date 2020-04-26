import os
import subprocess
from os.path import join, isfile

from config import config


def rename(filename, body_name, timestamp, latitude=None, longitude=None):
    screenshots_dir = config['screenshots_dir']
    filename = filename.split('\\')[-1]
    body_name = body_name.replace(' ', '_')
    timestamp = timestamp.replace(' ', '_').replace(':', '-')
    ext = filename.split('.')[-1]

    newfilename = f'{body_name}_{timestamp}.{ext}'

    if latitude and longitude:
        coordinates = f'{latitude:.2f}_{longitude:.2f}'.replace('.', '_')
        newfilename = f'{body_name}_({coordinates})_{timestamp}.{ext}'

    file = join(screenshots_dir, filename)
    newfile = join(screenshots_dir, newfilename)

    if not isfile(file):
        return False

    try:
        os.rename(file, newfile)
    except OSError:
        return False

    return newfilename


def convert_to_png(filename):
    screenshots_dir = config['screenshots_dir']
    file_path = join(screenshots_dir, filename)

    subprocess.Popen(
        ['python', 'convert_to_png.py', file_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
