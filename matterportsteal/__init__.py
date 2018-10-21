import sys
import os
import argparse
from urllib import request
from urllib import parse
from bs4 import BeautifulSoup
import json
import subprocess
import math

def pars_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--url",
        "-u",
        type=str,
        help="Download URL")

    parser.add_argument(
        "--dir",
        "-d",
        type=str,
        default = None,
        help="Save directory if none is specified title will be used")

    parser.add_argument(
        "--rot",
        "-r",
        type=str,
        default = 0,
        help = "Panorama rotation in degree")

    parser.add_argument(
        "--disable-download",
        "-dd",
        action = "store_true",
        help = "Disables Download")

    args = parser.parse_args()
    args = vars(args)

    if not args["url"]:
        print("+ + + Please provide URL + + +")
        parser.print_help()
        sys.exit(0)

    return args

def get_url_data(url, directory):
    # Load Data from URL
    soup_from_url = BeautifulSoup(request.urlopen(url).read(), "html.parser")
    pano_data = json.loads(soup_from_url.script.contents[0][33:-1])

    print("Downloading: " + soup_from_url.title.string)

    # Create Directory if none is specified
    if directory is None:
        directory = soup_from_url.title.string
        directory = directory.replace(" - Matterport 3D Showcase", "")
    dl_url = create_dl_url(pano_data)

    return dl_url, directory

def create_dl_url(pano_data):
    # URL Download Creation
    template_dl_url = pano_data["files"]["templates"][0]
    pano_metadata = json.loads(pano_data["model"]["images"][-1]["metadata"])
    scan_id = pano_metadata["scan_id"]
    custom_url_part = "tiles/" + scan_id + "/2k_face$i_$j_$k.jpg"
    dl_url = template_dl_url.replace("{{filename}}", custom_url_part)
    return dl_url

def dl_tiles(dl_url, directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

    picture_count = 0
    for i in range(0,6):
        for j in range(0,4):
            for k in range(0,4):
                file_number = str(i) + "_" + str(k) + "_" + str(j)
                temp_dl_url = dl_url.replace("$i_$j_$k", file_number)
                request.urlretrieve(temp_dl_url, directory + \
                                    "/" + "part-" + str(i) + "-1-" + \
                                    str(j) + "_" + str(k) + ".jpg")
                picture_count += 1
                print("Downloading Picture: " + str(picture_count) + "/96" + "\r", sep=' ', end='', flush=True)
    print("Downloading Picture: " + str(picture_count) + "/96")

def create_cube(directory, rotation):
    print("Creating cube")
    rc = subprocess.check_call(["./matterport_dl.sh",
                                str(directory),
                                str(int(math.degrees(rotation)))])


def main():
    args = pars_args()
    directory = args["dir"]
    rotation = math.radians(-float(args["rot"]))
    dl_url, directory = get_url_data(args["url"], directory)
    if not args["disable_download"]:
        dl_tiles(dl_url, directory)
    create_cube(directory, rotation)

if __name__ == "__main__":
    main()
