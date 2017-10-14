# img2ply
Convert an image sequence to a PLY point cloud.

![alt text](https://github.com/robertjoosten/img2ply/raw/master/data/header.png "Header")

## Installation
Using pip **NOT SUPPORTED YET**:

    pip install img2ply

If you prefer to install from source code use:

    cd img2ply/
    python setup.py install

## Usage
From the command line:

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

The package can also be used as a library:
```python
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
```

## Test
Test conversion can be done by running the following code, it will loop over all of the images in the images directory and create a pumpkin.ply file.
    
    cd img2ply/tests
    python convert.py

![alt text](https://github.com/robertjoosten/img2ply/raw/master/data/pumpkin.png "Pumpkin")



















