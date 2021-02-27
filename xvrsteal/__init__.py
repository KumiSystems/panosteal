import PIL.Image
import urllib.request
import io
import math
import subprocess
import tempfile
import pathlib
import os
from stitching import tiles_to_equirectangular_blender, multistitch

def xvr_normalize(url):
    '''
    Takes the URL of any image in a xvr panorama and returns a string
    with substitutable variables for image IDs.

    :param url: URL of an image contained in a xvr panorama
    :return: string with substitutable variables or False if URL invalid
    '''

    try:
        with urllib.request.urlopen(url) as res:
            assert res.getcode() == 200

        parts = url.split("/")

        assert "_" in parts[-1]
        parts[-1] = "%s.jpg"

        return "/".join(parts)

    except:
        return False

def xvr_export_simple(url):
    '''
    Exports xvr panoramas which only consist of six complete tiles. Takes
    the URL of one of these images and returns a list of PIL.Image objects

    :param url: URL of one of the images
    :return: list of PIL.Image objects
    '''

    output = []

    for i in ["posz", "posx", "negz", "negx", "posy", "negy"]:
        cur = url[:-8] + i + url[-4:]
        res = urllib.request.urlopen(cur)
        assert res.getcode() == 200
        fo = io.BytesIO(res.read())
        output += [PIL.Image.open(fo)]

    return output

def xvr_to_equirectangular(url, rotation=[0,0,0], resolution=[3840,1920]):
    '''
    Takes the URL of any image in a xvr panorama and returns a finished
    stitched image.

    :param url: Image URL
    :return: PIL.Image object containing the final image
    '''

    stitched = xvr_export_simple(url)
    function = tiles_to_equirectangular_blender

    rx, ry, rz = rotation
    width, height = resolution
    return function(*stitched, rx=rx, ry=ry, rz=rz, width=width, height=height)

process_url = xvr_to_equirectangular
