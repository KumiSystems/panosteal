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

        return f"{parts[0]}=x%i-y%i-z%i"

    except:
        return False

def google_getmaxzoom(schema):
    '''
    Takes a normalized string from google_normalize() and returns the maximum
    zoom level available.

    :param schema: normalized URL format output by google_normalize()
    :return: int value of largest available zoom level
    '''

    l = 0

    while True:
        try:
            url = schema % (0, 0, l+1)
            with urllib.request.urlopen(url) as res:
                assert res.getcode() == 200
                l += 1
        except:
            return l

def google_export(schema):
    '''
    Takes a normalized string from google_normalize() and returns a list of
    lists of lists containing all images fit for passing into stitch().

    :param schema: normalized URL format output by google_normalize()
    :return: list of lists of lists of PIL.Image() objects for multistitch()
    '''

    maxzoom = google_getmaxzoom(schema)
    output = []

    y = 0

    while True:
        r_array = []
        x = 0

        while True:
            try:
                res = urllib.request.urlopen(schema % (x, y, maxzoom))
                assert res.getcode() == 200
                fo = io.BytesIO(res.read())
                img = PIL.Image.open(fo)
                r_array.append(img)
                x += 1
            except Exception:
                break

        if not r_array:
            break

        output.append(r_array)
        y += 1

    return output

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
    images = google_export(schema)

    return stitch(images)

process_url = google_to_equirectangular
