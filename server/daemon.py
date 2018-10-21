import cgi
from server.connections import Request, Response
import mimetypes
import handler
import uuid
import configparser
import os
import glob
import hashlib
import time

HTTP200 = "200 OK"
HTTP202 = "202 Accepted"
HTTP400 = "400 Bad Request"
HTTP404 = "404 File Not Found"
HTTP405 = "405 Method Not Allowed"
HTTP500 = "500 Internal Server Error"

HTML = "text/html"
JSON = "application/json"
XML = "text/xml"
TEXT = "text/plain"
PNG = "image/png"

def static(req):
    try:
        content = open("server/static/" + req.endpoint, "rb").read()
        code = HTTP200
        ctype = mimetypes.guess_type(req.endpoint)[0]
    except:
        code = HTTP404
        content = "<h1>404 File Not Found</h1>"
        content += """The file you requested was not found on the server.
        Check the URL maybe?"""
        ctype = HTML
        content = content.encode()

    return Response(code, ctype, content)

def addjob(req):
    jobid = str(uuid.uuid4())
    config = configparser.ConfigParser()

    try:
        title = re.sub(r"[^a-zA-Z0-9_\-]", "_", req.args["title"][0]) or output
    except:
        title = "output"

    try:
        rx = int(req.args["rx"][0]) or 0
    except:
        rx = 0

    try:
        ry = int(req.args["ry"][0]) or 0
    except:
        ry = 0

    try:
        rz = int(req.args["rz"][0]) or 0
    except:
        rz = 0

    try:
        width = int(req.args["width"][0]) or 3840
    except:
        width = 3840

    try:
        height = int(req.args["height"][0]) or 1920
    except:
        height = 1920

    config["Job"] = {
            "url": req.args["url"][0],
            "title": title,
            "rx": rx,
            "ry": ry,
            "rz": rz,
            "width": width,
            "height": height
            }

    with open("/tmp/panosteal/" +  jobid, "w") as outfile:
        config.write(outfile)

    content = jobid.encode()
    ctype = TEXT
    status = HTTP200

    return Response(status, ctype, content)

def getjob(req):
    jobid = req.path[-1]
    content_disposition = None

    found = glob.glob("/tmp/panosteal/%s---*.png" % jobid)

    if found:
        md5 = "Not happening."
        while True:
            content = open(found[0], "rb").read()
            newmd5 = hashlib.md5(content).hexdigest()
            if newmd5 == md5:
                break
            md5 = newmd5
            time.sleep(0.5)

        code = HTTP200
        ctype = PNG
        content_disposition = found[0].split("---")[-1]

    elif glob.glob("/tmp/panosteal/%s*err" % jobid):
        content = "<h1>500 Internal Server Error</h1>".encode()
        code = HTTP500
        ctype = HTML

    elif not os.path.isfile("/tmp/panosteal/%s" % jobid):
        content = "<h1>404 File Not Found</h1>".encode()
        code = HTTP404
        ctype = HTML
    else:
        content = "".encode()
        code = HTTP202
        ctype = TEXT

    res = Response(code, ctype, content)

    if content_disposition:
        res.addHeader("Content-Disposition", 'attachment; filename="%s"' % content_disposition)
    return res

def application(env, re):
    req = Request(env)

    if req.endpoint.lower() == "addjob":
        handler = addjob
    elif req.endpoint.lower() == "getjob":
        handler = getjob
    else:
        handler = static

    res = handler(req)
    re(res.status, res.headers)
    yield res.content

