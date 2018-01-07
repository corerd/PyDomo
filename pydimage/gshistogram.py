#!/usr/bin/env python

# The MIT License (MIT)
#
# Copyright (c) 2015 Corrado Ubezio
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

'''Convert images to greyscale and save with histogram.

Basic Image Handling and Processing
Chapter 1.
https://www.safaribooksonline.com/library/view/programming-computer-vision/9781449341916/ch01.html
'''
from __future__ import print_function

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from pilib import ExtendedImage


def gshistogram(src_image_file, interactive=False):
    '''Convert image to greyscale and save with histogram as PNG.

    WARNING: At present matplotlib.pyplot.savefig() returns the error
    "TypeError: integer argument expected, got float"
    when saving as JPG.
    '''
    # read source image to array
    #gsimg = np.array(ExtendedImage(src_image_file).greyscale())
    gsimg_raw = ExtendedImage(src_image_file).greyscale()
    gsimg = np.array(gsimg_raw)

    # Creates a figure and three axes subplot on the same row:
    # picture, histogram and histogram outline curve.
    fig, (ax_pic, ax_hist, ax_outline) = plt.subplots(1, 3)
    plt.gray()  # don't use colors
    # plot the picture
    ax_pic.imshow(gsimg)
    ax_pic.axis('off')  # clear x- and y-axes

    # plot the histogram
    ax_hist.hist(gsimg.flatten(),128)

    # plot the histogram outline curve
    hg = gsimg_raw.histogram()
    # hg is a list of pixel counts, one for each pixel value in the source image.
    # Since the source image has one only band (greyscale),
    # hg contains 256 pixel counts, that is an index for each shade of grey.
    ax_outline.plot(hg, color='b')

    if interactive is True:
        plt.show()
    else:
        # Save the figure
        src_image_name, image_extension = os.path.splitext(src_image_file)
        dst_image_file = src_image_name + '_grey.png'
        print('Save greyscale image to:\n%s' % dst_image_file)
        fig.savefig(dst_image_file)


if __name__ == "__main__":
    for infile in sys.argv[1:]:
        gshistogram(infile, False)
