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

'''Compare performance between PIL and OpenCV'''

from __future__ import print_function

import os
import sys
import cv2
from PIL import Image
from time import time
from pilib import ExtendedImage as pilImage
from cvlib import ExtendedImage as cvImage


class Benchmark(object):

    def __init__(self, bmClass):
        self.imageClass = bmClass
        self.runs = 0
        self.deltat_min = sys.maxint
        self.deltat_max = 0
        self.elapsedt = 0

    def run(self, src_image_file):
        '''Compute the spent time
        converting a color image to greyscale
        and returning the pixel counts (histogram).
        '''
        self.runs = self.runs + 1
        #img = self.imageClass(src_image_file).greyscale()
        img = self.imageClass(src_image_file)
        deltat = time()
        img.greyscale()
        pixel_counts = img.histogram()
        deltat = time() - deltat
        if self.deltat_min > deltat:
            self.deltat_min = deltat
        if self.deltat_max < deltat:
            self.deltat_max = deltat
        self.elapsedt = self.elapsedt + deltat

    def report(self):
        print('Read %d pictures in %f seconds' % (self.runs, self.elapsedt))
        print('deltat min: %fs' % self.deltat_min)
        print('deltat max: %fs' % self.deltat_max)
        print('deltat average %fs:' % (self.elapsedt / self.runs))


class Benchmark_PIL(object):

    def __init__(self):
        self.runs = 0
        self.deltat_min = sys.maxint
        self.deltat_max = 0
        self.elapsedt = 0
        self.width_ave = 0
        self.height_ave = 0

    def run(self, src_image_file):
        '''Compute the spent time
        converting a color image to greyscale
        and returning the pixel counts (histogram).
        '''
        self.runs = self.runs + 1
        img = Image.open(src_image_file)
        width, height = img.size
        self.width_ave = self.width_ave + width
        self.height_ave = self.height_ave + height
        deltat = time()
        img = img.convert(mode='L')
        pixel_counts = img.histogram()
        deltat = time() - deltat
        if self.deltat_min > deltat:
            self.deltat_min = deltat
        if self.deltat_max < deltat:
            self.deltat_max = deltat
        self.elapsedt = self.elapsedt + deltat

    def report(self):
        print('Read %d %dx%d pictures in %f seconds' %
            (self.runs, (self.width_ave/self.runs), (self.height_ave/self.runs), self.elapsedt))
        print('deltat min: %fs' % self.deltat_min)
        print('deltat max: %fs' % self.deltat_max)
        print('deltat average %fs:' % (self.elapsedt / self.runs))


class Benchmark_OpenCV(object):

    def __init__(self):
        self.runs = 0
        self.deltat_min = sys.maxint
        self.deltat_max = 0
        self.elapsedt = 0
        self.width_ave = 0
        self.height_ave = 0

    def run(self, src_image_file):
        '''Compute the spent time
        converting a color image to greyscale
        and returning the pixel counts (histogram).
        '''
        self.runs = self.runs + 1
        #img = cv2.imread(src_image_file, cv2.IMREAD_GRAYSCALE)
        img = cv2.imread(src_image_file)
        height, width = img.shape[:2]
        self.width_ave = self.width_ave + width
        self.height_ave = self.height_ave + height
        deltat = time()
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        pixel_counts = cv2.calcHist([img],[0],None,[256],[0,256])
        deltat = time() - deltat
        if self.deltat_min > deltat:
            self.deltat_min = deltat
        if self.deltat_max < deltat:
            self.deltat_max = deltat
        self.elapsedt = self.elapsedt + deltat

    def report(self):
        print('Read %d %dx%d pictures in %f seconds' %
            (self.runs, (self.width_ave/self.runs), (self.height_ave/self.runs), self.elapsedt))
        print('deltat min: %fs' % self.deltat_min)
        print('deltat max: %fs' % self.deltat_max)
        print('deltat average %fs:' % (self.elapsedt / self.runs))


if __name__ == "__main__":
    if len(sys.argv[1:]) > 0:
        imagePathName = sys.argv[1]
    else:
        imagePathName = '.'
    if os.path.isdir(imagePathName):
        # iterate top directory listing
        bmPIL = Benchmark(pilImage)
        bmPIL_native = Benchmark_PIL()
        bmCV = Benchmark(cvImage)
        bmCV_native = Benchmark_OpenCV()
        print('Running...')
        for dirname, dirnames, filenames in os.walk(imagePathName):
            for imageFileName in filenames:
                if imageFileName.lower().endswith('.jpg'):
                    bmPIL.run(os.path.join(dirname, imageFileName))
                    bmPIL_native.run(os.path.join(dirname, imageFileName))
                    bmCV.run(os.path.join(dirname, imageFileName))
                    bmCV_native.run(os.path.join(dirname, imageFileName))
            break  # only top directory listing
        print('\nPIL stats:')
        bmPIL.report()
        print('\nOpenCV stats:')
        bmCV.report()
        print('\nPIL native stats:')
        bmPIL_native.report()
        print('\nOpenCV native stats:')
        bmCV_native.report()
    else:
        print('Directory required')
