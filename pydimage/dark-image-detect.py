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

'''Detecting black images on python

Basic Image Handling and Processing
Chapter 1.
https://www.safaribooksonline.com/library/view/programming-computer-vision/9781449341916/ch01.html
'''
from __future__ import print_function

import os
import sys
from errno import ENOENT
import cv2
from PIL import Image


def isDarkImage(image_file):
    '''Return True if in the histogram of the image_file there are
    more 'dark' pixels (first 128 values in a greyscale representation)
    than 'light' ones.

    See: https://stackoverflow.com/a/8659785
    '''
    img = Image.open(image_file)
    gsimg = img.convert(mode='L')
    hg = gsimg.histogram()
    # count should be 256 most/all of the time (an index for each shade of grey)
    count = len(hg)

    if sum(hg[:count/2]) > sum(hg[count/2:]):
        return True
    return False


def listDarkImage(src_image_file, interactive=False):
    img = cv2.imread(src_image_file)
    if img is None:
        # OpenCV imread function doesn't raise an exception if the file doesn't exist,
        # then provide '[Errno 2] No such file or directory' IOError exception.
        raise IOError(ENOENT, "%s: '%s'" % (os.strerror(ENOENT), src_image_file))
    gsimg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # convert to greyscale

    # Get the pixel counts, one for each pixel value in the source image.
    # Since the source image has one only band (greyscale),
    # there are 256 pixel counts, that is an index for each shade of grey.
    pixel_counts = cv2.calcHist([gsimg],[0],None,[256],[0,256])

    # In a greyscale representation, the first 128 values are 'dark' pixels,
    # the last 128 are 'light' ones.
    indexes = len(pixel_counts)  # should be 256 (an index for each shade of grey)
    dark_pixels = sum(pixel_counts[:indexes/2])
    light_pixels = sum(pixel_counts[indexes/2:])

    cv2.putText(gsimg,'Dark pixels: %d' % dark_pixels, (1,30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, 255)
    cv2.putText(gsimg,'Light pixels: %d' % light_pixels, (1,60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, 255)

    # Save the figure
    src_image_name, image_extension = os.path.splitext(src_image_file)
    dst_image_file = src_image_name + '_grey.jpg'
    print('Save greyscale image to:\n%s' % dst_image_file)
    cv2.imwrite(dst_image_file, gsimg)

    if interactive is True:
        # Display the figure
        cv2.imshow(os.path.basename(src_image_file), gsimg)
        while True:
            k = cv2.waitKey(0) & 0xFF
            if k == 27: break             # ESC key to exit
        cv2.destroyAllWindows()


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
                    listDarkImage(os.path.join(dirname, imageFileName))
            break  # only top directory listing
    else:
        listDarkImage(imagePathName, True)
