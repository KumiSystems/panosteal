import PIL.Image
import urllib.request
import io
import math
import subprocess
import tempfile
import pathlib
import os
from stitching import tiles_to_equirectangular_blender, multistitch

def giraffe_normalize(url):
    '''
    Takes the URL of any image in a Giraffe360 panorama and returns a string
    with substitutable variables for image IDs.

    :param url: URL of an image contained in a Giraffe360 panorama
    :return: string with substitutable variables or False if URL invalid
    '''

    try:
        with urllib.request.urlopen(url) as res:
            assert res.getcode() == 200

        parts = url.split("/")

        assert "_" in parts[-1]
        assert parts[-1][0] == "l"

        parts[-1] = "l%i_%s_%s_%s.jpg"

        return "/".join(parts)

    except:
        return False

def giraffe_getmaxzoom(schema):
    '''
    Takes a normalized string from giraffe_normalize() and returns the maximum
    zoom level available.

    :param schema: normalized URL format output by giraffe_normalize()
    :return: int value of largest available zoom level
    '''

    l = 0

    while True:
        try:
            url = schema % (l+1, "f", "01", "01")
            with urllib.request.urlopen(url) as res:
                assert res.getcode() == 200
                l += 1
        except:
            return l

def giraffe_export(schema):
    '''
    Takes a normalized string from giraffe_normalize() and returns a list of
    lists of lists containing all images fit for passing into stitch().

    :param schema: normalized URL format output by giraffe_normalize()
    :return: list of lists of lists of PIL.Image() objects for multistitch()
    '''

    maxzoom = giraffe_getmaxzoom(schema)
    output = []

    for tile in "frblud":
        t_array = []
        y = 1

        while True:
            r_array = []
            x = 1

            while True:
                try:
                    res = urllib.request.urlopen(schema % (maxzoom, tile, str(y).zfill(2), str(x).zfill(2)))
                    assert res.getcode() == 200
                    fo = io.BytesIO(res.read())
                    img = PIL.Image.open(fo)
                    r_array.append(img)
                    x += 1
                except urllib.error.HTTPError:
                    break
                except Exception:
                    raise

            if not r_array:
                break

            t_array.append(r_array)
            y += 1

        output.append(t_array)

    return output

def giraffe_make_tiles(url):
    '''
    Determines the type of processing needed to build the six tiles, then
    creates and returns them.

    :param urL: URL of any image in a Giraffe360 panorama
    :return: list of stitched PIL.Image objects (back, right, front, left, top,
             bottom)
    '''

    parts = url.split("/")

    try:
        schema = giraffe_normalize(url)
        images = giraffe_export(schema)
        return multistitch(images)

    except:
        raise
        raise ValueError("%s does not seem to be a valid Giraffe360 URL." % url)

def giraffe_to_equirectangular(url, rotation=[0,0,0], resolution=[3840,1920]):
    '''
    Takes the URL of any image in a Giraffe360 panorama and returns a finished
    stitched image.

    :param url: Image URL
    :return: PIL.Image object containing the final image
    '''

    stitched = giraffe_make_tiles(url)
    function = tiles_to_equirectangular_blender

    rx, ry, rz = rotation
    width, height = resolution
    return function(*stitched, rx=rx, ry=ry, rz=rz, width=width, height=height)

process_url = giraffe_to_equirectangular
