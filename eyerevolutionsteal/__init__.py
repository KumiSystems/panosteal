import PIL.Image
import urllib.request
import io
import math
import subprocess
import tempfile
import pathlib
import os
from stitching import tiles_to_equirectangular_blender, multistitch

def eyerevolution_normalize(url):
    '''
    Takes the URL of any image in a eyerevolution panorama and returns a string
    with substitutable variables for image IDs.

    :param url: URL of an image contained in a eyerevolution panorama
    :return: string with substitutable variables or False if URL invalid
    '''

    try:
        with urllib.request.urlopen(url) as res:
            assert res.getcode() == 200

        parts = url.split("/")

        assert "_" in parts[-1]
        parts[-1] = "l%i_%s_%i_%i.jpg"
        parts[-2] = "%i"
        parts[-3] = "l%i"
        parts[-4] = "%s"

        return "/".join(parts)

    except:
        return False

def eyerevolution_getmaxzoom(schema):
    '''
    Takes a normalized string from eyerevolution_normalize() and returns the maximum
    zoom level available.

    :param schema: normalized URL format output by eyerevolution_normalize()
    :return: int value of largest available zoom level
    '''

    l = 1

    while True:
        try:
            url = schema % ("f", l+1, 1, l+1, "f", 1, 1)
            with urllib.request.urlopen(url) as res:
                assert res.getcode() == 200
                l += 1
        except:
            return l

def eyerevolution_export(schema):
    '''
    Takes a normalized string from eyerevolution_normalize() and returns a list of
    lists of lists containing all images fit for passing into stitch().

    :param schema: normalized URL format output by eyerevolution_normalize()
    :return: list of lists of lists of PIL.Image() objects for multistitch()
    '''

    # /{cube}/l{zoom}/{y}/l{zoom}_{cube}_{y}_{x}.jpg

    maxzoom = eyerevolution_getmaxzoom(schema)
    output = []

    for tile in "frblud":
        t_array = []
        y = 1

        while True:
            r_array = []
            x = 1

            while True:
                try:
                    # raise Exception(schema % (tile, maxzoom, y, maxzoom, tile, y, x))
                    res = urllib.request.urlopen(schema % (tile, maxzoom, y, maxzoom, tile, y, x))
                    assert res.getcode() == 200
                    fo = io.BytesIO(res.read())
                    img = PIL.Image.open(fo)
                    r_array.append(img)
                    x += 1
                except Exception as e:
                    # raise
                    break

            if not r_array:
                break

            t_array.append(r_array)
            y += 1

        output.append(t_array)

    return output

def eyerevolution_export_simple(url):
    '''
    Exports eyerevolution panoramas which only consist of six complete tiles. Takes
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

def eyerevolution_make_tiles(url):
    '''
    Determines the type of processing needed to build the six tiles, then
    creates and returns them.

    :param urL: URL of any image in a eyerevolution panorama
    :return: list of stitched PIL.Image objects (back, right, front, left, top,
             bottom)
    '''

    parts = url.split("/")

    try:
        if "pano_" in parts[-1]:
           return eyerevolution_export_simple(url)
        else:
           schema = eyerevolution_normalize(url)
           images = eyerevolution_export(schema)
           return multistitch(images)

    except:
        raise
        raise ValueError("%s does not seem to be a valid eyerevolution URL." % url)


def eyerevolution_to_equirectangular(url, rotation=[0,0,0], resolution=[3840,1920]):
    '''
    Takes the URL of any image in a eyerevolution panorama and returns a finished
    stitched image.

    :param url: Image URL
    :return: PIL.Image object containing the final image
    '''

    stitched = eyerevolution_make_tiles(url)
    function = tiles_to_equirectangular_blender

    rx, ry, rz = rotation
    width, height = resolution
    return function(*stitched, rx=rx, ry=ry, rz=rz, width=width, height=height)

process_url = eyerevolution_to_equirectangular
