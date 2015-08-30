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


'''This module wraps the Dropbox Uploader BASH script.

It needs Dropbox Uploader.
Ref: https://github.com/andreafabrizi/Dropbox-Uploader
'''


from utils.extcmd import ExtCmdRunError, runcmd


def dropbox_upload(local_file, remote_file):
    '''Upload a local file to a remote Dropbox folder.

    Returns success
    '''
    success = False
    uploadcmd = 'dropbox_uploader.sh upload %s %s' % (local_file, remote_file)
    retcode = -1
    cmdoutput = ''
    print 'Uploading', local_file
    try:
        retcode, cmdoutput = runcmd(uploadcmd)
    except ExtCmdRunError as e:
        cmdoutput = 'ExtCmdRunError: {0}'.format(e)
    if retcode == 0:
        success = True
    if len(cmdoutput) > 0:
        #print the output of the external command
        for outLine in cmdoutput.splitlines():
            print 'runcmd: {0}'.format(outLine)
    return success