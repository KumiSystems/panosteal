import sys
import os
from urllib import request
from urllib import parse
from bs4 import BeautifulSoup
import json
import subprocess
import math
import io
import PIL.Image
from stitching import multistitch, tiles_to_equirectangular_blender

def get_url_data(url):
    # Load Data from URL
    soup_from_url = BeautifulSoup(request.urlopen(url).read(), "html.parser")
    pano_data = json.loads(soup_from_url.script.contents[0][33:-1])

    return create_dl_url(pano_data)

def create_dl_url(pano_data):
    # URL Download Creation
    template_dl_url = pano_data["files"]["templates"][0]
    pano_metadata = json.loads(pano_data["model"]["images"][-1]["metadata"])
    scan_id = pano_metadata["scan_id"]
    custom_url_part = "tiles/" + scan_id + "/2k_face$i_$j_$k.jpg"
    dl_url = template_dl_url.replace("{{filename}}", custom_url_part)
    return dl_url

def dl_tiles(dl_url):
    output = []

    for i in range(0,6):
        i_array = []

        for j in range(0,4):
            j_array = []

            for k in range(0,4):
                file_number = str(i) + "_" + str(k) + "_" + str(j)
                temp_dl_url = dl_url.replace("$i_$j_$k", file_number)
                res = request.urlopen(temp_dl_url)
                assert res.getcode() == 200
                fo = io.BytesIO(res.read())
                img = PIL.Image.open(fo)
                j_array.append(img)

            i_array.append(j_array)

        output.append(i_array)

    return output

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
