#!/usr/bin/env python3

import re
import importlib
import argparse
import subprocess
import traceback

regs = {
        r"\d+/\d+/\d+_\d+\.jpg": "krpanosteal",
        r"\_[frblud].jpg": "krpanosteal",
        r"my.matterport.com/show/": "matterportsteal",
        r"cdn-1.matterport.com": "matterportsimple",
        r"youtube.com": "youtubesteal",
        r"l\d_[frblud]_\d\d_\d\d.jpg": "giraffesteal",
        r"=x\d-y\d-z\d": "googlesteal",
        r"[brflud]\/\d\/\d_\d\.jpg": "tdvsteal",
        "c\d_l\d_\d_\d.jpg": "pindorasteal",
        "/[frblud]/l\d/\d/l\d_[frblud]_\d_\d.jpg": "eyerevolutionsteal",
        "(pos|neg)[xyz]\.jpg": "xvrsteal",
       }


def parse_url(url):
    global regs

    selected = None

    for regex, handler in regs.items():
        if re.search(regex, url):
            selected = handler
            break

    if not selected:
        raise ValueError("No matching handler found")

    return importlib.import_module(selected).process_url

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('url', help='URL to process')
    parser.add_argument('--title', help='title to be used for the file name', default="No Title")
    parser.add_argument("--rotation", nargs=3, type=int, help="rotation on x/y/z axes", metavar=("x","y","z"))
    parser.add_argument("--resolution", type=int, nargs=2, metavar=("w","h"))
    parser.add_argument("--output", default=".")
    parser.add_argument("--module", help="name of module to use")

    args = parser.parse_args()

    try:
        handler = importlib.import_module(args.module).process_url if args.module else parse_url(args.url)
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
