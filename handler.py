#!/usr/bin/env python3

import re
import importlib
import argparse
import subprocess
import traceback

regs = {
        "\d/\d/\d_\d\.jpg": "krpanosteal",
        "pano\_[frblud].jpg": "krpanosteal",
        "my.matterport.com/show/": "matterportsteal",
        "youtube.com": "youtubesteal",
        "l\d_[frblud]_\d\d_\d\d.jpg": "giraffesteal"
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
    parser.add_argument('--title', help='title to be used for the file name', default="No Title")
    parser.add_argument("--rotation", nargs=3, type=int, help="rotation on x/y/z axes", metavar=("x","y","z"))
    parser.add_argument("--resolution", type=int, nargs=2, metavar=("w","h"))
    parser.add_argument("--output", default=".")

    args = parser.parse_args()

    try:
        handler = parse_url(args.url)
        image = handler(args.url, args.rotation or [0,0,0], args.resolution or [3840, 1920])
        if not hasattr(image, "im"):
            with open(args.output + "/" + args.title + ".mkv", "wb") as video:
                video.write(image)
            subprocess.run(["/usr/bin/ffmpeg",
                "-i", args.output + "/" + args.title + ".mkv", 
                "-ss", "00:00:10", 
                "-vframes", "1", 
                "-f", "image2", 
                args.output + "/" + args.title + ".thumb.jpg"])
        else:
            image.save(args.output + "/" + args.title + ".png")
    except Exception:
        with open(args.output + "/" + args.title + ".err", "w") as errorfile:
            errorfile.write(traceback.format_exc())
