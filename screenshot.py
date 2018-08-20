import os
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
        return newfilename
    except OSError:
        return False
