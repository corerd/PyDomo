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


import logging


# Globals
VERSION = '1.0'
DEFAULT_CFG_FILE = 'camrecordercfg.json'
LOG_FILE_NAME = 'camcorderlog.txt'


def mkdir(dir_name, verbose=False):
    """Create the directory named by dir_name.
    If verbose is true, displays the info messages,
    otherways logs them.

    Returns bool
    """
    from os import makedirs, path

    exists = True
    if not path.isdir(dir_name):
        try:
            info_message = 'Create directory %s' % dir_name
            if verbose is True:
                print info_message
            else:
                logging.info(info_message)
            makedirs(dir_name)
        except OSError:
            if not path.isdir(dir_name):
                # If the directory doesn't exist,
                # there was an error on creation
                exists = False
    return exists


def snap_shot(cfg):
    from cameraman.camgrab import imageCapture
    from datetime import datetime

    # Make the grabbed picture file path
    now = datetime.now()
    picturesDirName = '{0:s}/CAMSHOT_{1:%Y%m%d}'\
                                            .format(cfg.data['datastore'], now)
    if mkdir(picturesDirName) is False:
        logging.error('Error create directory %s' % picturesDirName)
        return 1

    nsnaps = 0
    print 'Taking snap shots...'
    cameraIndex = 0
    for camera in cfg.data['cameras-list']:
        pictureFileFullName = '{0:s}/CS{1:%Y%m%d_%H%M}_{2:02d}.jpg'\
                                    .format(picturesDirName, now, cameraIndex)
        if imageCapture(camera, pictureFileFullName) is False:
            logging.warning('Fail get image from camera %s' % camera['source'])
        else:
            nsnaps = nsnaps + 1
            logging.info('Save image %s' % pictureFileFullName)
        cameraIndex = cameraIndex + 1
    print 'Total %d snap shots' % nsnaps
    return 0


def parse_args():
    from os.path import dirname, realpath
    from argparse import ArgumentParser, RawTextHelpFormatter
    usage = """Take a snapshots from a bunch of cameras.
If none given, the configuration is read from the JSON file:
    %s
"""
    parser = ArgumentParser(description=(usage % DEFAULT_CFG_FILE),
                             formatter_class=RawTextHelpFormatter)
    print '%s v%s (C) 2015' % (parser.prog, VERSION)

    desc = "read the configuration from the CFG JSON file"
    def_cfg_file = '%s/%s' % (dirname(realpath(__file__)), DEFAULT_CFG_FILE)
    parser.add_argument('-c', '--cfg', dest='cfg_file',
                            help=desc,
                            default=def_cfg_file)
    parser.add_argument('-v', '--version', action='version',
                        version='%%(prog)s %s' % VERSION)
    args = parser.parse_args()
    return args


def main():
    from camrecordercfg import ConfigDataLoad

    options = parse_args()
    print 'Read configuration from file:', options.cfg_file

    try:
        cfg_data = ConfigDataLoad(options.cfg_file)
    except:
        print 'Unable to load config'
        return 1

    # Make the container warking directory
    warking_dir = cfg_data.data['datastore']
    if mkdir(warking_dir, verbose=True) is False:
        print 'Error create directory', warking_dir
        return 1

    logging.basicConfig(filename=warking_dir + '/' + LOG_FILE_NAME,
                        format='%(asctime)s %(levelname)s %(message)s',
                        level=logging.DEBUG)

    return snap_shot(cfg_data)


if __name__ == "__main__":
    exit(main())
