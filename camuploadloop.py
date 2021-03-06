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


'''Loop forever taking a snap shot from a camera and uploading to the cloud.
'''

import camupload
from time import sleep
from datetime import datetime

HOUR_START = 8
HOUR_END = 18
IDLE_TIME_SECONDS = 60 * 60  # 60 min


def todayAt(today, hr, min=0, sec=0, micros=0):
    '''Inspired from:
    http://stackoverflow.com/a/9716793
    '''
    return today.replace(hour=hr, minute=min, second=sec, microsecond=micros)


def run():
    '''Returns status code
    '''
    while True:
        now = datetime.now()
        if now >= todayAt(now, HOUR_START) and now < todayAt(now, HOUR_END):
            camupload.run()
        m, s = divmod(IDLE_TIME_SECONDS, 60)
        h, m = divmod(m, 60)
        print '%s: wait %d hours, %02d minutes, %02d seconds' % \
                                                   (now, h, m, s)
        sleep(IDLE_TIME_SECONDS)
    return 0


if __name__ == "__main__":
    exit(run())
