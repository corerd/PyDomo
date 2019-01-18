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

"""Get configuration parameters
"""
from __future__ import print_function

import json
import errno
from os import makedirs, strerror
from os.path import dirname, exists


class ConfigDataLoad:
    def __init__(self, loadFile, defaultData=''):
        self.jsonFile = loadFile
        self.data = ''
        try:
            json_data = open(self.jsonFile)
            self.data = json.load(json_data)
            json_data.close()
        except:
            # loadFile doesn't exist,
            # use defaultData if provided
            # otherwise raise the exception
            if len(defaultData) > 0:
                self.data = json.loads(json.dumps(defaultData))
            else:
                raise

    def update(self):
        if len(self.data) <= 0:
            return
        if checkDatastore(self.jsonFile) is not True:
            # No such file or directory
            raise OSError(errno.ENOENT, strerror(errno.ENOENT))
        with open(self.jsonFile, "w") as f:
            f.write(json.dumps(self.data))


def checkDatastore(dir_name):
    """If the directory dir_name doesn't exist, create it.
    Returns True for SUCCESS, False otherwise
    """
    success = True
    if not exists(dirname(dir_name)):
        try:
            makedirs(dirname(dir_name))
        except OSError as exc:
            # Guard against race condition
            # See: http://stackoverflow.com/a/12517490
            if exc.errno != errno.EEXIST:
                success = False
    return success


def getDatastorePath(json_file):
    datastorePath = ''
    try:
        cfg = ConfigDataLoad(json_file)
        datastorePath = cfg.data['datastore']
    except:
        pass
    return datastorePath


if __name__ == "__main__":
    datastorePath = getDatastorePath('cloudcfg.json.template')
    if len(datastorePath) <= 0:
        print('ERROR: datastore path not found')
    else:
        print(datastorePath)
