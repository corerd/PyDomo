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

'''OpenCV (CV2) wrapper for matplotlib

References:
https://extr3metech.wordpress.com/2012/09/23/convert-photo-to-grayscale-with-python-opencv/
http://www.bogotobogo.com/python/OpenCV_Python/python_opencv3_matplotlib_rgb_brg_image_load_display_save.php
http://www.bogotobogo.com/python/OpenCV_Python/python_opencv3_image_histogram_calcHist.php
'''
from __future__ import print_function

import cv2
from numpy import float32


class ExtendedImage(object):

    def __init__(self, imageFileName):
        '''Opens and identifies the given image file.
        OpenCV returns an uint8 image while matplotlib requires float32.
        '''
        self.__VERSION__ = 'OpenCV ' + cv2.__version__
        self._img = cv2.imread(imageFileName).astype(float32)

    def __getattr__(self, key):
        '''Delegate (almost) everything to self._img'''
        if key == '_img':
            #  http://nedbatchelder.com/blog/201010/surprising_getattr_recursion.html
            raise AttributeError()
        return getattr(self._img, key)

    def save(self, fileName):
        cv2.imwrite(fileName, self._img)

    def greyscale(self):
        '''Convert to greyscale'''
        self._img = cv2.cvtColor(self._img, cv2.COLOR_BGR2GRAY)
        return self

    def histogram(self):
        '''Get the pixel counts, one for each pixel value in the source image.
        Assuming the source image has one only band (greyscale),
        there are 256 pixel counts, that is an index for each shade of grey.

        TODO color image
        '''
        return cv2.calcHist([self._img],[0],None,[256],[0,256])


def convert2greyscale(src_image_file):
    '''Make a greyscale copy of the source image_file'''
    src_image_name, image_extension = os.path.splitext(src_image_file)
    dst_image_file = src_image_name + '_grey' + image_extension
    print('Save greyscale image to:\n%s' % dst_image_file)
    gsimg = ExtendedImage(src_image_file).greyscale()
    gsimg.save(dst_image_file)


if __name__ == "__main__":
    '''test ExtendedImage Class'''
    import os
    import sys

    if len(sys.argv[1:]) > 0:
        imagePathName = sys.argv[1]
    else:
        imagePathName = '.'
    if os.path.isdir(imagePathName):
        # iterate top directory listing
        # and get all files ending with '.jpg'
        for dirname, dirnames, filenames in os.walk(imagePathName):
            for imageFileName in filenames:
                if imageFileName.lower().endswith('.jpg'):
                    convert2greyscale(os.path.join(dirname, imageFileName))
            break  # only top directory listing
    else:
        convert2greyscale(imagePathName)
