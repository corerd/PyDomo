#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

'''PyDomo Web server using built in Python web support and
Jinja2 engine to render Bootstrap templates
'''

from __future__ import print_function

from os.path import dirname, join, realpath
from utils.cli import cfg_file_arg
from PyDomoApp import PyDomoApp
from utils.configdataload import ConfigData


# Globals
VERSION = '1.0'
DEFAULT_CFG_FILE = 'PyDomoSvr.json'

DEFAULT_CFG_FILE_PATH = join(dirname(realpath(__file__)), DEFAULT_CFG_FILE)

USAGE = '''PyDomo Web Server


If no configuration file path is given, it will read:
    %s
''' % DEFAULT_CFG_FILE_PATH


def main():
    conf = ConfigData()
    options = cfg_file_arg(VERSION, USAGE, DEFAULT_CFG_FILE_PATH)
    try:
        conf.load(options.cfg_file)
        app = PyDomoApp(conf.data, debug=options.debug)
    except:
        print("Errors found")
        return 1

    if options.debug is True:
        print('Debug support is enabled')
    app.run()


if __name__ == "__main__":
    exit(main())
