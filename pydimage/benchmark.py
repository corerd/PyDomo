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
        self.runs = self.runs + 1
        deltat = time()
        img = self.imageClass(src_image_file).greyscale()
        img.histogram()
        deltat = time() - deltat
        if self.deltat_min > deltat:
            self.deltat_min = deltat
        if self.deltat_max < deltat:
            self.deltat_max = deltat
        self.elapsedt = self.elapsedt + deltat

    def report(self):
        print('Runs:', self.runs)
        print('Time:', self.elapsedt)
        print('deltat_min:', self.deltat_min)
        print('deltat_max:', self.deltat_max)
        print('deltat_med:', self.elapsedt / self.runs)


if __name__ == "__main__":
    if len(sys.argv[1:]) > 0:
        imagePathName = sys.argv[1]
    else:
        imagePathName = '.'
    if os.path.isdir(imagePathName):
        # iterate top directory listing
        bmPIL = Benchmark(pilImage)
        bmCV = Benchmark(cvImage)
        print('Running...')
        for dirname, dirnames, filenames in os.walk(imagePathName):
            for imageFileName in filenames:
                if imageFileName.lower().endswith('.jpg'):
                    bmPIL.run(os.path.join(dirname, imageFileName))
                    bmCV.run(os.path.join(dirname, imageFileName))
            break  # only top directory listing
        print('\nPIL stats:')
        bmPIL.report()
        print('\nOpenCV stats:')
        bmCV.report()
    else:
        print('Directory required')
