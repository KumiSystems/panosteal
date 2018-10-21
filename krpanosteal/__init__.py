import PIL.Image
import urllib.request
import io
import math
import subprocess
import tempfile
import pathlib
import os
from stitching import tiles_to_equirectangular_blender, multistitch

def krpano_normalize(url):
    '''
    Takes the URL of any image in a krpano panorama and returns a string
    with substitutable variables for image IDs.

    :param url: URL of an image contained in a krpano panorama
    :return: string with substitutable variables or False if URL invalid
    '''

    try:
        with urllib.request.urlopen(url) as res:
            assert res.getcode() == 200

        parts = url.split("/")

        assert "_" in parts[-1]
        parts[-1] = "%i_%i.jpg"
        parts[-2] = "%i"
        parts[-3] = "%i"

        return "/".join(parts)

    except:
        return False

def krpano_getmaxzoom(schema):
    '''
    Takes a normalized string from krpano_normalize() and returns the maximum
    zoom level available.

    :param schema: normalized URL format output by krpano_normalize()
    :return: int value of largest available zoom level
    '''

    l = 0

    while True:
        try:
            url = schema % (0, l+1, 0, 0)
            with urllib.request.urlopen(url) as res:
                assert res.getcode() == 200
                l += 1
        except:
            return l

def krpano_export(schema):
    '''
    Takes a normalized string from krpano_normalize() and returns a list of
    lists of lists containing all images fit for passing into stitch().

    :param schema: normalized URL format output by krpano_normalize()
    :return: list of lists of lists of PIL.Image() objects for multistitch()
    '''

    maxzoom = krpano_getmaxzoom(schema)
    output = []

    for tile in range(6):
        t_array = []
        y = 0

        while True:
            r_array = []
            x = 0

            while True:
                try:
                    res = urllib.request.urlopen(schema % (tile, maxzoom, y, x))
                    assert res.getcode() == 200
                    fo = io.BytesIO(res.read())
                    img = PIL.Image.open(fo)
                    r_array.append(img)
                    x += 1
                except Exception as e:
                    break

            if not r_array:
                break

            t_array.append(r_array)
            y += 1

        output.append(t_array)

    return output

def krpano_export_simple(url):
    '''
    Exports krpano panoramas which only consist of six complete tiles. Takes
    the URL of one of these images and returns a list of PIL.Image objects

    :param url: URL of one of the images
    :return: list of PIL.Image objects
    '''

    output = []

    for i in "frblud":
        cur = url[:-5] + i + url[-4:]
        res = urllib.request.urlopen(cur)
        assert res.getcode() == 200
        fo = io.BytesIO(res.read())
        output += [PIL.Image.open(fo)]

    return output

def krpano_make_tiles(url):
    '''
    Determines the type of processing needed to build the six tiles, then
    creates and returns them.

    :param urL: URL of any image in a krpano panorama
    :return: list of stitched PIL.Image objects (back, right, front, left, top,
             bottom)
    '''

    parts = url.split("/")

    try:
        if "pano_" in parts[-1]:
           return krpano_export_simple(url)
        else:
           schema = krpano_normalize(url)
           images = krpano_export(schema)
           return multistitch(images)

    except:
        raise
        raise ValueError("%s does not seem to be a valid krpano URL." % url)


def krpano_to_equirectangular(url, rotation=[0,0,0], resolution=[0,0]):
    '''
    Takes the URL of any image in a krpano panorama and returns a finished
    stitched image.

    :param url: Image URL
    :return: PIL.Image object containing the final image
    '''

    stitched = krpano_make_tiles(url)
    function = tiles_to_equirectangular_blender

    rx, ry, rz = rotation
    width, height = resolution
    return function(*stitched, rx=rx, ry=ry, rz=rz, width=width, height=height)

process_url = krpano_to_equirectangular
