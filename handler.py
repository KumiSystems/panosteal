#!/usr/bin/env python3

import re
import importlib

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
    url = input("Please input the URL of an image. ")
    handler = parse_url(url)
    image = handler(url)
    image.save("out.png")
