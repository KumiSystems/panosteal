import PIL.Image
import urllib.request
import io
import math
import subprocess
import tempfile
import pathlib
import os
import subprocess
import uuid
import glob

from stitching import tiles_to_equirectangular_blender, multistitch

def youtube_get_video(url):
        vid = uuid.uuid4().hex
        with open("/tmp/" + vid, "w") as logfile:
            process = subprocess.Popen(
                ['youtube-dl',
                    '--user-agent', '""',
                    '-o', vid,
                    "--merge-output-format", "mkv",
                    url,
                    ], 
                cwd="/tmp/panosteal/youtube/",
                stdout=logfile,
                stderr=logfile
                )

            process.wait()

        try:
            data = open('/tmp/panosteal/youtube/%s.mkv' % vid, 'rb').read()
        except:
            try:
                data = open('/tmp/panosteal/youtube/%s.mp4' % vid, 'rb').read()
            except:
                try:
                    data = open('/tmp/panosteal/youtube/%s.webm' % vid, 'rb').read()
                    process2 = subprocess.Popen(
                            ['ffmpeg',
                                '-i', '%s.webm' % vid,
                                '-c:v', "copy",
                                '%s.mkv' % vid],
                            cwd="/tmp/panosteal/youtube/"
                            )
                except:
                    raise

        for i in glob.glob("/tmp/panosteal/youtube/%s*" % vid):
            os.remove(i)

        return data

def youtube_get_file(yurl):
    urllib.request.urlopen(yurl)

def youtube_to_equirectangular(url, rotation=[0,0,0], resolution=[3840,1920]):
    '''
    Takes the URL of any YouTube video, downloads it and returns the video file.

    :param url: YouTube URL
    :return: File object containing the video
    '''

    rx, ry, rz = rotation
    width, height = resolution

    return youtube_get_video(url)

process_url = youtube_to_equirectangular
