import sys
import os
from urllib import request
from urllib import parse
import subprocess
import math
import io
import PIL.Image
from stitching import multistitch, tiles_to_equirectangular_blender
from matterportsteal import dl_tiles

def get_url_data(url):
    return url.rsplit("/", 1)[0] + "/2k_face$i_$j_$k.jpg?" + url.rsplit("?")[-1]

def matterport_make_tiles(url):
    dl_url = get_url_data(url)
    images = dl_tiles(dl_url)
    return multistitch(images)

def matterport_to_equirectangular(url, rotation=[0,0,0], resolution=[3840,1920]):
    stitched = matterport_make_tiles(url)
    function = tiles_to_equirectangular_blender

    ordered = stitched[1:5] + [stitched[0], stitched[5]]

    rx, ry, rz = rotation
    width, height = resolution
    return function(*ordered, rx=rx, ry=ry, rz=rz, width=width, height=height)

process_url = matterport_to_equirectangular
