import PIL.Image
import urllib.request
import io
import math
import subprocess
import tempfile
import pathlib
import os
import re

from stitching import stitch, tiles_to_equirectangular_blender

def steal3dvista_normalize(url):
    '''
    Takes the URL of any image in a steal3dvista panorama and returns a string
    with substitutable variables for image IDs.

    :param url: URL of an image contained in a steal3dvista panorama
    :return: string with substitutable variables or False if URL invalid
    '''

    try:
        with urllib.request.urlopen(url) as res:
            assert res.getcode() == 200

        parts = url.split("/")

        assert "_" in parts[-1]
        parts[-1] = "%i_%i.jpg"
        parts[-2] = "%i"

        return "/".join(parts)

    except:
        return False


def steal3dvista_getmaxzoom(schema):
    '''
    Takes a normalized string from steal3dvista_normalize() and returns the maximum
    zoom level available.

    :param schema: normalized URL format output by steal3dvista_normalize()
    :return: int value of largest available zoom level
    '''

    return 0


def steal3dvista_export(schema):
    '''
    Takes a normalized string from steal3dvista_normalize() and returns a list of
    lists of lists containing all images fit for passing into stitch().

    :param schema: normalized URL format output by steal3dvista_normalize()
    :return: list of lists of lists of PIL.Image() objects for multistitch()
    '''

    maxzoom = steal3dvista_getmaxzoom(schema)
    output = []

    if True:
        y = 0
        while True:
            r_array = []
            x = 0

            while True:
                try:
                    res = urllib.request.urlopen(schema % (maxzoom, y, x))
                    assert res.getcode() == 200
                    fo = io.BytesIO(res.read())
                    img = PIL.Image.open(fo)
                    r_array.append(img)
                    x += 1
                except Exception as e:
                    break

            if not r_array:
                break

            output.append(r_array)
            y += 1

    return output


def steal3dvista_make_tiles(url):
    '''
    Determines the type of processing needed to build the six tiles, then
    creates and returns them.

    :param urL: URL of any image in a steal3dvista panorama
    :return: list of stitched PIL.Image objects (back, right, front, left, top,
             bottom)
    '''

    parts = url.split("/")

    try:
        schema = steal3dvista_normalize(url)
        images = steal3dvista_export(schema)
        full = stitch(images)
       
        tiles = []

        for i in range(6):
            tiles.append(full.crop((full.width / 12 * i, 0, (full.width / 12 * (i + 1)) - 1, full.height)))

        return [tiles[4], tiles[0], tiles[5], tiles[1], tiles[2], tiles[3]]

    except:
        raise ValueError("%s does not seem to be a valid steal3dvista URL." % url)


def steal3dvista_to_equirectangular(url, rotation=[0,0,0], resolution=[3840,1920]):
    '''
    Takes the URL of any image in a steal3dvista panorama and returns a finished
    stitched image.

    :param url: Image URL
    :return: PIL.Image object containing the final image
    '''

    stitched = steal3dvista_make_tiles(url)
    function = tiles_to_equirectangular_blender

    rx, ry, rz = rotation
    width, height = resolution
    return function(*stitched, rx=rx, ry=ry, rz=rz, width=width, height=height)


process_url = steal3dvista_to_equirectangular
