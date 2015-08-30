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


'''This module wraps subprocess allowing to run external commands.
'''

from subprocess import check_output, CalledProcessError, STDOUT


class ExtCmdRunError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "{0}".format(self.value)


def runcmd(cmd):
    retcode = 0
    cmdOutput = ''
    try:
        cmdOutput = check_output(cmd, stderr=STDOUT, shell=True)
    except OSError as e:
        raise ExtCmdRunError(e)
    except CalledProcessError as e:
        # Exception raised when a process returns a non-zero exit status
        retcode = e.returncode
        cmdOutput = e.output
    return retcode, cmdOutput


if __name__ == "__main__":
    print 'runcmd with normal process termination'
    exitStatus, output = runcmd("ls")
    print exitStatus
    print output
    print 'runcmd when a process returns a non-zero exit status'
    exitStatus, output = runcmd("ls non_existent_file")
    print exitStatus
    print output
    print 'runcmd with non existent command'
    exitStatus, output = runcmd('non_existent_command')
    print exitStatus
    print output
    print 'runcmd reporting ShellError'
    exitStatus, output = runcmd('cd some_non_existing_dir')
    print exitStatus
    print output

