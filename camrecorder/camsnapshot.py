#!/usr/bin/env python
#
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

from __future__ import print_function

import logging
from os.path import dirname, join, realpath


# Globals
VERSION = '1.0'
DEFAULT_CFG_FILE = 'camrecordercfg.json'
LOG_FILE_NAME = 'camcorderlog.txt'

DEFAULT_CFG_FILE_PATH = join(dirname(realpath(__file__)), DEFAULT_CFG_FILE)

USAGE = """Take a snapshots from a bunch of cameras.
If none given, the configuration is read from the JSON file:
    %s
""" % DEFAULT_CFG_FILE_PATH


def mkdir(dir_name, verbose=False):
    """Create the directory named by dir_name.
    If verbose is true, displays the info messages,
    otherways logs them.

    Returns bool
    """
    from os import mkdir, path

    exists = True
    if not path.isdir(dir_name):
        try:
            info_message = 'Create directory %s' % dir_name
            if verbose is True:
                print(info_message)
            else:
                logging.info(info_message)
            # Creates the directory in a secure manner
            mkdir(dir_name, 0o700)
        except OSError:
            if not path.isdir(dir_name):
                # If the directory doesn't exist,
                # there was an error on creation
                exists = False
    return exists


def snap_shot(cfg):
    '''Takes a snap shot from each camera in the list,
    and saves the image in a file with the following path name:
        <datastore-path>/SNAPSHOT_yymmdd/S_yymmdd_HHMMSS_XX.jpg
    where yymmdd and HHMMSS is current local date and time in the format:
        yy  is the year without century as a decimal number [00,99].
        mm  is the month as a decimal number [01,12].
        dd  is the day of the month as a decimal number [01,31].
        HH  is the hour (24-hour clock) as a decimal number [00,23].
        MM  is the minute as a decimal number [00,59].
        SS  is the second as a decimal number [00,59].

        XX  is the camera index as a decimal number [00,99].
    '''
    from cameraman.camgrab import imageCapture
    from datetime import datetime

    # Make the grabbed picture file path
    picturesDirName = '{0:s}/SNAPSHOT_{1:%y%m%d}'\
                                        .format(cfg.data['datastore'],
                                                 datetime.now())
    if mkdir(picturesDirName) is False:
        logging.error('Error create directory %s' % picturesDirName)
        return 1

    nsnaps = 0
    print('Taking snap shots...')
    cameraIndex = 0
    for camera in cfg.data['cameras-list']:
        pictureFileFullName = '{0:s}/S_{1:%y%m%d_%H%M%S}_{2:02d}.jpg'\
                                    .format(picturesDirName,
                                        datetime.now(),
                                         cameraIndex)
        if imageCapture(camera, pictureFileFullName) is False:
            logging.error('get image from camera %s' % camera['source'])
        else:
            nsnaps = nsnaps + 1
            logging.info('Save image %s' % pictureFileFullName)
        cameraIndex = cameraIndex + 1
    print('Total %d snap shots' % nsnaps)
    return 0


def main():
    from utils.cli import cfg_file_arg
    from camrecorder.camrecordercfg import ConfigDataLoad

    options = cfg_file_arg(VERSION, USAGE, DEFAULT_CFG_FILE_PATH)
    print('Read configuration from file:', options.cfg_file)

    try:
        cfg_data = ConfigDataLoad(options.cfg_file)
    except:
        print('Unable to load config')
        return 1

    # Make the container warking directory
    warking_dir = cfg_data.data['datastore']
    if mkdir(warking_dir, verbose=True) is False:
        print('Error create directory', warking_dir)
        return 1

    logging.basicConfig(filename=warking_dir + '/' + LOG_FILE_NAME,
                        format='%(asctime)s %(levelname)s %(message)s',
                        level=logging.DEBUG)

    return snap_shot(cfg_data)


if __name__ == "__main__":
    exit(main())
