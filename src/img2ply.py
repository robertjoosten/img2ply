"""			
Convert an image sequence to a PLY point cloud.

Installation
============
Using pip
::
    pip install img2ply
    
If you prefer to install from source code use
::
    cd img2ply/
    python setup.py install
    
Usage
=====
From the command line
::
    img2ply -h
    
    img2ply [-h] -o PLY -bb BOUNDINGBOX BOUNDINGBOX BOUNDINGBOX
       [--depthDirection DEPTHDIRECTION] [--depthInverse DEPTHINVERSE]
       [--ignoreAlpha IGNOREALPHA] [--widthSamples WIDTHSAMPLES]
       [--heightSamples HEIGHTSAMPLES]
       [--maintainAspectRatio MAINTAINASPECTRATIO]
       input

input:                  path to image sequence
-o:                     output file path
-bb:                    bounding box of object in x, y, z
--depthDirection:       direction in which the slices are facing
--depthInverse:         reverse the placement of the slices
--ignoreAlpha:          ignore pixels with an alpha value below 25
--widthSamples:         amount of width samples, if 0 every pixel is sampled
--heightSamples:        amount of height samples, if 0 every pixel is sampled
--maintainAspectRatio:  maintain aspect ratio of sample points   

The package can also be used as a library
::
    import img2ply
    img2ply.convert(
        input, 
        ply, 
        bb,
        direction="z", 
        inverse=False,
        ignoreAlpha=True,
        wSamples=0, 
        hSamples=0, 
        maintainAspectRatio=True
    )

Code
====
"""

import os
import time
import argparse
import fileinput
from PIL import Image

# ----------------------------------------------------------------------------

SUPPORTED_FILE_EXTENSION = ["png", "jpg"]
PLY_HEADER = """ply
format ascii 1.0
element vertex <VERTEXCOUNT>
property float x
property float y
property float z
property uchar red
property uchar green
property uchar blue
end_header
"""

# ----------------------------------------------------------------------------

def boolType(v):
    """
    This function can be parsed into the type of an argparse add argument.
    It's a hack but needed to add boolean attributes in a more intuative way.

    :param v:
    :return: True/False
    :rtype: bool
    """
    return v.lower() in ["yes", "true", "t", "1"]

# ----------------------------------------------------------------------------

def getPositionMapper(direction):
    """
    Based on the depth direction the indices of the world position are ordered
    to match the users input.

    :param str direction: Acceptable arguments are 'x', 'y' and 'z'
    :return: List of indices
    :rtype: list
    """
    # variables
    order = []

    # build order
    if direction == "x":
        order = [2, 1, 0]
    elif direction == "y":
        order = [0, 2, 1]
    elif direction == "z":
        order = [0, 1, 2]

    # build mapper
    return order

# ----------------------------------------------------------------------------

def getImageSequence(input):
    """
    List the content of the input directory and filter through it and find
    all of the supported file extensions. Once this list is created it will
    be sorted. This means that it's very important to number your image
    sequence before conversion

    :param str input: Input directory
    :return: Ordered list of images
    :rtype: list
    """
    # get variable
    images = []

    # list dir
    files = os.listdir(input)
    files.sort()

    # loop dir
    for f in files:
        # get extension
        _, ext = os.path.splitext(f)

        # validate extension
        if not ext[1:].lower() in SUPPORTED_FILE_EXTENSION:
            continue

        # add images
        images.append(os.path.join(input, f))

    return images

def getImageData(
    f,
    ignoreAlpha=True,
    wSamples=0, hSamples=0, maintainAspectRatio=True
):
    """
    Read the image and resize it based on the sample arguments, if the sample
    arguments are not set every pixel will be processed. When maintaining the
    aspect ratio the width will have priority over the height.

    :param str f: File path to image
    :param bool ignoreAlpha: Skip pixel is alpha is < 25
    :param int wSamples: Number of width sample points
    :param int hSamples: Number of height sample points
    :param maintainAspectRatio:
    :return: Normalized 2D point and colour information
    :rtype: list(tuple(position, colour))
    """
    data = []

    # open image
    image = Image.open(f)

    # get aspect ratio
    width, height = image.size
    aspectRatio = float(height)/float(width)

    # get samples with aspect ratio
    if wSamples and maintainAspectRatio:
        hSamples = int(wSamples*aspectRatio)
    elif hSamples and maintainAspectRatio:
        wSamples = int(hSamples*(1/aspectRatio))

    # get sample from with and height
    if not wSamples:
        wSamples = width
    if not hSamples:
        hSamples = height

    # resize image
    image.thumbnail((wSamples, hSamples), Image.ANTIALIAS)

    # loop pixels
    for x in range(wSamples):
        for y in range(hSamples):
            r, g, b, a = image.getpixel((x,y))

            if a < 25 and ignoreAlpha:
                continue

            data.append(([x/float(wSamples), y/float(hSamples)],[r,g,b]))

    return data

# ----------------------------------------------------------------------------

def divider():
    return "-" * 50

def convert(
    input, ply, bb,
    direction="z", inverse=False,
    ignoreAlpha=True,
    wSamples=0, hSamples=0, maintainAspectRatio=True
):
    """
    Read the input directory and find all of the images of the supported file
    extensions. This list is sorted and will then have its pixels processed
    and stored in a PLY file format. All of the pixels will be mapped onto a
    bounding box that is provided by the user. This bounding box is a list in
    the following axis; x, y and z. The direction determines what depth
    direction is, the depth direction is the direction travelled between each
    images. This direction can be reversed if needed. The amount of samples
    can be adjusted to lower the resolution of the point cloud, in case the
    images are very high resolution the point cloud size can be adjusted by
    changing the amount of samples. If no samples are specified the images
    resolution will be used.

    :param str input: Input directory
    :param str ply: Output filepath
    :param list bb: Bounding box; x, y, z
    :param str direction: Depth direction
    :param bool inverse: Inverse depth direction
    :param bool ignoreAlpha: Skip pixel is alpha is < 25
    :param int wSamples: Number of width sample points
    :param int hSamples: Number of height sample points
    :param maintainAspectRatio:
    """
    # variables
    t = time.time()
    totalPoints = 0

    # get conversion dict
    mapper = getPositionMapper(direction)
    if not mapper:
        raise RuntimeError(
            "Invalid depth direction! Valid arguments: 'x', 'y' or 'z'"
        )

    # get direction multiplier
    multiplier = -1 if inverse else 1

    # get images
    sequence = getImageSequence(input)
    length = len(sequence)
    if not length:
        raise RuntimeError(
            "No Image sequence found!"
        )
        
    print divider()
    print "Images Found:    {0}".format(length)
    
    # get mapper data
    wI, hI, dI = mapper
    wB, hB, dB = bb[wI], bb[hI], bb[dI]
    
    print divider()
    print "Width Index:     {0}".format(wI)
    print "Height Index:    {0}".format(hI)
    print "Depth Index:     {0}".format(dI)
    
    print divider()
    print "Start Processing Images"
    print divider()

    # write point cloud
    with open(ply, "w") as f:
        # write header
        f.write(PLY_HEADER)

        # get image data
        for i, image in enumerate(sequence):
            # process image
            data = getImageData(
                image,
                ignoreAlpha,
                wSamples,
                hSamples,
                maintainAspectRatio
            )
            
            # process data
            for pos, colour in data:
                # map position in 3 dimensions
                position = [0, 0, 0]
                position[wI] = wB * pos[0]
                position[hI] = hB * pos[1]
                position[dI] = (dB/length) * i * multiplier

                # get strings
                # rounding positions to 3 decimals
                posString = [str(round(p,3)) for p in position]
                colourString = [str(c) for c in colour]

                # write data
                f.write("{0}\n".format(" ".join(posString + colourString)))
                totalPoints += 1
                
            countString = "< {0} / {1} >".format(i + 1, length).ljust(20)
            pointString = "Points Written: {0}".format(totalPoints).ljust(20)
            print countString, pointString

    # update header
    print divider()
    print "Updating header with vertex count: {0}".format(totalPoints)
    f = fileinput.FileInput(ply, inplace=True)
    for line in f:
        print line.replace("<VERTEXCOUNT>", str(totalPoints)),
    f.close()

    # print duration and output path
    diff = time.time() - t
    print divider()
    print "Output:          {0}".format(ply)
    print "Duration:        {0} min".format(round(diff/60,1))

def main():
    # create parser
    parser = argparse.ArgumentParser(
        description="Convert an image sequence to a PLY point cloud"
    )

    # add required argument
    extensions = ", ".join(SUPPORTED_FILE_EXTENSION)
    parser.add_argument(
        "input", 
        help="path to image sequence"
    )

    # add required named arguments
    required = parser.add_argument_group("required arguments")
    required.add_argument(
        "-o", "--ply",
        required=True,
        help="output file path"
    )
    required.add_argument(
        "-bb", "--boundingBox",
        nargs=3,
        type=float,
        required=True,
        help="bounding box of object in x, y, z"
    )

    # add optional named arguments
    parser.add_argument(
        "--depthDirection",
        type=str,
        default="z",
        help="direction in which the slices are facing"
    )

    parser.add_argument(
        "--depthInverse", 
        type=boolType, 
        default=False,
        help="reverse the placement of the slices"
    )
    parser.add_argument(
        "--ignoreAlpha", 
        type=boolType, 
        default=True,
        help="ignore pixels with an alpha value below 25"
    )
    parser.add_argument(
        "--widthSamples", 
        type=int, 
        default=0,
        help="amount of width samples, if 0 every pixel is sampled"
    )
    parser.add_argument(
        "--heightSamples", 
        type=int, 
        default=0,
        help="amount of height samples, if 0 every pixel is sampled"
    )
    parser.add_argument(
        "--maintainAspectRatio", 
        type=boolType, 
        default=True,
        help="maintain aspect ratio of sample points"
    )

    # parse arguments
    args = parser.parse_args()

    # convert
    convert(
        args.input,
        args.ply,
        args.boundingBox,
        args.depthDirection,
        args.depthInverse,
        args.ignoreAlpha,
        args.widthSamples,
        args.heightSamples,
        args.maintainAspectRatio
    )

if __name__ == "__main__":
    main()
