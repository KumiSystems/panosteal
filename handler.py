#!/usr/bin/env python3

import re
import importlib
import argparse

regs = {
        "\d/\d/\d_\d\.jpg": "krpanosteal",
        "pano\_[frblud].jpg": "krpanosteal"
       }


def parse_url(url):
    global regs

    selected = None

    for regex, handler in regs.items():
        if re.search(regex, url):
            selected = handler
            break

    if not selected:
        raise ValueError("No handler known for this URL. Kaggi.")

    return importlib.import_module(selected).process_url

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('url', help='URL to process')
    parser.add_argument('--title', help='title to be used for the file name')
    parser.add_argument("--rotation", nargs=3, type=int, help="rotation on x/y/z axes", metavar=("x","y","z"))
    parser.add_argument("--resolution", type=int, nargs=2, metavar=("w","h"))
    parser.add_argument("--output")

    args = parser.parse_args()

    try:
        handler = parse_url(args.url)
        image = handler(args.url, args.rotation or [0,0,0], args.resolution or [3840, 1920])

        image.save(args.output + "/" + args.title + ".png")
    except Exception as e:
        with open(args.output + "/" + args.title + ".err", "w") as errorfile:
            errorfile.write("")
