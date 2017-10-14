import os
import img2ply

if __name__ == "__main__": 
    # get path
    path = os.path.split(__file__)[0]
    
    # get input and output
    input = os.path.join(path, "images")
    ply = os.path.join(path, "pumpkin.ply")
    
    # convert
    img2ply.convert(
        input, 
        ply, 
        [15.0, 10.0, 15.0],
        direction="y", 
        inverse=True,
        ignoreAlpha=True,
        wSamples=0, 
        hSamples=0, 
        maintainAspectRatio=True
    )