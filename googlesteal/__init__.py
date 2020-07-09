import PIL.Image
import urllib.request
import io
import math
import subprocess
import tempfile
import pathlib
import os
from stitching import stitch

def google_normalize(url):
    '''
    Takes the URL of any image in a google panorama and returns a string
    with substitutable variables for image IDs.

    :param url: URL of an image contained in a google panorama
    :return: string with substitutable variables or False if URL invalid
    '''

    try:
        with urllib.request.urlopen(url) as res:
            assert res.getcode() == 200

        parts = url.split("=")

        return f"{parts[0]}=w16000"

    except:
        return False

def google_to_equirectangular(url, rotation=[0,0,0], resolution=[3840,1920]):
    '''
    Takes the URL of any image in a google panorama and returns a finished
    stitched image.

    :param url: Image URL
    :return: PIL.Image object containing the final image
    '''

    if not "=x" in url:
        raise ValueError(f"{url} does not seem to be a valid Google URL." % url)

    schema = google_normalize(url)
    res = urllib.request.urlopen(schema)
    assert res.getcode() == 200
    return PIL.Image.open(io.BytesIO(res.read()))

process_url = google_to_equirectangular
