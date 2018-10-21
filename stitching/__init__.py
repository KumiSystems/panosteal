import tempfile
import pathlib
import os
import subprocess
import PIL.Image
import math

def tiles_to_equirectangular_blender(back, right, front, left, top, bottom,
        rx=0, ry=0, rz=0, tmp=None, height=1920, width=3840, keep=False):

    '''
    Use Blender to convert the images into an equirectangular format. This
    requires both Blender and cube2sphere to be installed and in $PATH.

    Will create a temporary directory to store files in if no working directory
    is passed (tmp). The function will return a PIL.Image object containing the
    final equirectangular image.

    :param back: PIL.Image containing the "back" part of the cube map
    :param right: PIL.Image containing the "right" part of the cube map
    :param front: PIL.Image containing the "front" part of the cube map
    :param left: PIL.Image containting the "left" part of the cube map
    :param top: PIL.Image containing the "top" part of the cube map
    :param bottom: PIL.Image containing the "bottom" part of the cube map
    :param rx: Rotation in degrees (integer) to apply on the x axis
    :param ry: Rotation in degrees (integer) to apply on the y axis
    :param rz: Rotation in degrees (integer) to apply on the z axis
    :param tmp: Temporary directory to use. Will create one if None is passed
    :param height: Target height of the output image
    :param width: Target width of the output image
    :param keep: Will not clean up temporary directory if True
    :return: PIL.Image object containing the equirectangular image
    '''

    tmpdir = tempfile.TemporaryDirectory()
    
    if tmp and not keep:
        tmpdir.name = tmp
    if not tmp:
        tmp = tmpdir.name

    '''Blender needs actual files rather than PIL objects, so create a folder
    for those.'''

    try:
        pathlib.Path(tmp).mkdir(parents=True, exist_ok=True)
    except:
        print("Failed to create temporary directory.")
        print(tmp)
        raise

    '''If no resolution is passed, assume the original resolution for output.'''

    if not height and not width:
        height = height or left.size[0] * 2
        width = width or left.size[0] * 4

    '''Move to temporary directory and create files for Blender to work with.'''

    pre = os.getcwd()
    os.chdir(tmp)

    left.save("left.png")
    front.save("front.png")
    right.save("right.png")
    back.save("back.png")
    bottom.save("bottom.png")
    top.save("top.png")

    try:
        process = subprocess.Popen(
            ['cube2sphere',
                'front.png', 
                'back.png', 
                'right.png', 
                'left.png',
                'top.png', 
                'bottom.png',
                '-R', str(rx), str(ry), str(rz), # rotation on x/y/z axes
                '-o', 'out',
                '-f', 'png',
                "-r", str(width), str(height)]
            )

        process.wait()

        outimg = PIL.Image.open("%s/out0001.png" % tmp) # Read new image to PIL

        os.chdir(pre) # Move back to previous working directory

        if not keep:
            tmpdir.cleanup() # Delete temporary directory to free space

        # Flip the output image as inputs seem to be flipped. Return the image.
        return outimg.transpose(PIL.Image.FLIP_LEFT_RIGHT)

    except:
        os.chdir(pre)
        print("Something went wrong trying to convert to equirectangular.")
        raise

def tiles_to_equirectangular(back, right, front, left, top, bottom):
    '''
    Use Blender to convert the images into an equirectangular format. This does
    not require Blender to be installed, instead using a custom algorithm. This
    is not tested thoroughly and will probably not work at this point.

    The function will return a PIL.Image object containing the final 
    equirectangular image.

    :param back: PIL.Image containing the "back" part of the cube map
    :param right: PIL.Image containing the "right" part of the cube map
    :param front: PIL.Image containing the "front" part of the cube map
    :param left: PIL.Image containting the "left" part of the cube map
    :param top: PIL.Image containing the "top" part of the cube map
    :param bottom: PIL.Image containing the "bottom" part of the cube map
    :return: PIL.Image object containing the equirectangular image
    '''

    dim = left.size[0]

    raw = []

    t_width = dim * 4
    t_height = dim * 2

    for y in range(t_height):
        v = 1.0 - (float(y) / t_height)
        phi = v * math.pi

        for x in range(t_width):
            u = float(x) / t_width
            theta = u * math.pi * 2

            x = math.cos(theta) * math.sin(phi)
            y = math.sin(theta) * math.sin(phi)
            z = math.cos(phi)

            a = max(abs(x), abs(y), abs(z))

            xx = x / a
            yy = y / a
            zz = z / a

            if yy == -1:
                currx = int(((-1 * math.tan(math.atan(x / y)) + 1.0) / 2.0) * dim)
                ystore = int(((-1 * math.tan(math.atan(z / y)) + 1.0) / 2.0) * (dim - 1))
                part = left

            elif xx == 1:
                currx = int(((math.tan(math.atan(y / x)) + 1.0) / 2.0) * dim)
                ystore = int(((math.tan(math.atan(z / x)) + 1.0) / 2.0) * dim)
                part = front

            elif yy == 1:
                currx = int(((-1 * math.tan(math.atan(x / y)) + 1.0) / 2.0) * dim)
                ystore = int(((math.tan(math.atan(z / y)) + 1.0) / 2.0) * (dim - 1))
                part = right

            elif xx == -1:
                currx = int(((math.tan(math.atan(y / x)) + 1.0) / 2.0) * dim)
                ystore = int(((-1 * math.tan(math.atan(z / x)) + 1.0) / 2.0) * (dim - 1))
                part = back

            elif zz == 1:
                currx = int(((math.tan(math.atan(y / z)) + 1.0) / 2.0) * dim)
                ystore = int(((-1 * math.tan(math.atan(x / z)) + 1.0) / 2.0) * (dim - 1))
                part = bottom

            else:
                currx = int(((-1 * math.tan(math.atan(y / z)) + 1.0) / 2.0) * dim)
                ystore = int(((-1 * math.tan(math.atan(x / z)) + 1.0) / 2.0) * (dim - 1))
                part = top

            curry = (dim - 1) if ystore > (dim - 1) else ystore

            if curry > (dim - 1):
                curry = dim - 1

            if currx > (dim - 1):
                currx = dim - 1

            raw.append(part.getpixel((currx, curry)))

    output = PIL.Image.new("RGB", (t_width, t_height))
    output.putdata(raw)

    return output

def multistitch(tiles):
    '''
    Takes a list of lists of lists containing PIL Image objects and stitches
    them into one. Each box tile (first-order lists), line (second-order) and
    column (third-order) must be equal in height and width.

    :param faces: list of lists of lists containing PIL.Image objects
    :return: list of stitched PIL.Image objects
    '''

    output = []

    for tile in tiles:
        output.append(stitch(tile))

    return output

def stitch(images):
    '''
    Takes a list of lists containing PIL Image objects and stitches them into
    one. Each line (first-order lists) and column (second-order) must be equal
    in height and width.

    :param images: list of lists containing PIL.Image objects
    :return: stitched PIL.Image object
    '''

    t_height = 0 # Total height of resulting image
    t_width = 0 # Total width of resulting image

    '''Calculate height of final image by adding up heights of the first images
    of each row.'''

    for row in images:
        w, h = row[0].size
        t_height += h

    '''Calculate width of final image by adding up widths of the images in the
    first row.'''

    for image in images[0]:
        w, h = image.size
        t_width += w

    '''Generate output Image object using calculated height and width.'''

    output = PIL.Image.new("RGB", (t_width, t_height))

    curry = 0 # Current y position (top = 0)

    for row in images:
        currx = 0 # Current x position (left = 0)
        y_offset = 0 # How far down we have to go for the next line

        for image in row:

            '''Paste line of images into the output image.'''

            output.paste(im=image, box=(currx, curry))
            w, h = image.size
            currx += w

            if not y_offset:
                y_offset = h

        curry += y_offset

    return output
