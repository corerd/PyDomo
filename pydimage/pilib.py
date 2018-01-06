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

'''Extend Python Imaging Library (PIL) wrapper

According to Fredrik Lundh, the author of PIL, the Image class isn't designed
to be subclassed by application code.
If you want custom behaviour, use a delegating wrapper.
See: https://stackoverflow.com/a/5165352
     https://mail.python.org/pipermail/image-sig/2006-March/003832.html
     http://effbot.org/pyfaq/what-is-delegation.htm
'''
from __future__ import print_function

from PIL import Image


class ExtendedImage(object):

    def __init__(self, imageFileName):
        '''Opens and identifies the given image file'''
        self._img = Image.open(imageFileName)

    def __getattr__(self, key):
        '''Delegate (almost) everything to self._img'''
        if key == '_img':
            #  http://nedbatchelder.com/blog/201010/surprising_getattr_recursion.html
            raise AttributeError()
        return getattr(self._img, key)

    def greyscale(self):
        '''Convert to greyscale'''
        return self._img.convert(mode='L')  #<-- ExtendedImage delegates to self._img


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

    for infile in sys.argv[1:]:
        convert2greyscale(infile)
