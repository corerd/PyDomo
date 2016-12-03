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


'''Command Line Interfaces utilities
'''


def cfg_file_arg(prog_version, prog_usage, default_cfg_file, prog_date='2015'):
    '''Parse cli arguments matching the following options:
         -h or --help
         -c or --cfg
         -d or --debug
         -v or --version

    Returns args
    '''
    from argparse import ArgumentParser, RawTextHelpFormatter

    parser = ArgumentParser(description=prog_usage,
                             formatter_class=RawTextHelpFormatter)
    print '%s v%s (C) %s' % (parser.prog, prog_version, prog_date)

    desc = "read the configuration from the CFG JSON file"
    parser.add_argument('-c', '--cfg', dest='cfg_file',
                            help=desc,
                            default=default_cfg_file)
    parser.add_argument('-d', '--debug', dest='debug', action='store_true',
                            help='enable debug',
                            default='False')
    parser.add_argument('-v', '--version', action='version',
                        version='%%(prog)s %s' % prog_version)
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    options = cfg_file_arg('X.Y', 'Usage string', 'default_cfg_file')
    print 'Configuration file:', options.cfg_file
    if options.debug is True:
        print 'Debug is Enable'
    else:
        print 'Debug is Disable'
