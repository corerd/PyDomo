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
from pilib import ExtendedImage as pilImage
from cvlib import ExtendedImage as cvImage


def imageHist(ax_row, img_raw):
    '''Drow picture and histograms in a subplots row'''
    img = np.array(img_raw)

    # plot the picture
    ax_row[0].imshow(img, cmap=plt.get_cmap('gray'))
    ax_row[0].axis('off')  # clear x- and y-axes
    ax_row[0].set_title(img_raw.__VERSION__)

    # plot matplotlib histogram
    ax_row[1].hist(img.flatten(),128)

    # Get the pixel counts, one for each pixel value in the source image.
    # Since the source image has one only band (greyscale),
    # there are 256 pixel counts, that is an index for each shade of grey.
    pixel_counts = img_raw.histogram()

    # In a greyscale representation, the first 128 values are 'dark' pixels,
    # the last 128 are 'light' ones.
    indexes = len(pixel_counts)  # should be 256 (an index for each shade of grey)
    dark_pixels = sum(pixel_counts[:indexes/2])
    light_pixels = sum(pixel_counts[indexes/2:])

    # plot the histogram outline curve
    # text in axis coords (0,0 is lower-left and 1,1 is upper-right)
    ax_row[2].plot(pixel_counts, color='b')
    ax_row[2].text(0.05, 0.95, 'DARK %d' % dark_pixels,
                    color='red',
                    transform=ax_row[2].transAxes)  # specify axis coords
    ax_row[2].text(0.05, 0.9, 'LIGHT %d' % light_pixels,
                    color='red',
                    transform=ax_row[2].transAxes)  # specify axis coords


def gshistogram(src_image_file, interactive=False):
    '''Convert image to greyscale both PIL and OpenCV
     and save with histograms as PNG.

    WARNING: At present matplotlib.pyplot.savefig() returns the error
    "TypeError: integer argument expected, got float"
    when saving as JPG.
    '''
    # Creates a figure with 2 rows of 3 subplots:
    #   picture, histogram and histogram outline curve.
    fig, axes = plt.subplots(2, 3, figsize=(11, 7))

    # read source image to array and Drow picture and histograms
    # in the respective subplots row
    imageHist(axes[0], pilImage(src_image_file).greyscale())
    imageHist(axes[1], cvImage(src_image_file).greyscale())

    if interactive is True:
        plt.show()
    else:
        # Save the figure
        src_image_name, image_extension = os.path.splitext(src_image_file)
        dst_image_file = src_image_name + '_grey.png'
        print('Save greyscale image to:\n%s' % dst_image_file)
        fig.savefig(dst_image_file)

    # Close the Figure instance fig
    plt.close(fig)


if __name__ == "__main__":
    if len(sys.argv[1:]) > 0:
        imagePathName = sys.argv[1]
    else:
        imagePathName = '.'
    if os.path.isdir(imagePathName):
        # iterate top directory listing
        for dirname, dirnames, filenames in os.walk(imagePathName):
            for imageFileName in filenames:
                if imageFileName.lower().endswith('.jpg'):
                    gshistogram(os.path.join(dirname, imageFileName))
            break  # only top directory listing
    else:
        gshistogram(imagePathName, True)
