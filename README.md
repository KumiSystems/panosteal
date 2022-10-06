# Panorama Image Exporter for 360 Content (PIX360)

PIX360, previously called panosteal, is a Python3 script allowing you to download 360° panorama images and videos from different sources on the Internet.

It was created as part of a project for one of our clients, with additional sources simply slapped on as required, so currently the code is neither clean nor documented. We are hoping to rewrite the application from scratch soon, but we don't know just how soon. In that rewrite, we would like to implement a couple of convenience features as well.

The script can be used by passing the URL of a *part* of the image you want to download into _handler.py_ – the script is not currently able to use the URL of a website to find embedded images (with two exceptions: images hosted by Google, and 360 videos on YouTube), so you will need to find the URL by using your browser's developer tools, for example.

It also comes with a simple HTTP server. To use it, make sure you have _gunicorn_ installed, then run *both* _hallmonitor.sh_ and _run.sh_.

## Install

To run PIX360, you need:

* Python >= 3.8
* Blender (for stitching images)

We recommend creating and enabling a venv, then installing the Python requirements using `pip install -r requirements.txt`.