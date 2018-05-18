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

'''Append to PYTHONPATH the path of the script from which it runs.
Ref. http://stackoverflow.com/a/7886092
'''
from __future__ import print_function

import sys
from random import randint
from datetime import datetime
from cloud.gmailer import send_mail


def main(argv):
    if len(argv) < 2 or len(argv) > 3:
        print('USAGE; emailsend_test <dest-address> [attachment]')
        return
    dest_address = argv[1]
    if len(argv) == 3:
        attached = argv[2]
    else:
        attached = ''

    print('>>> Send a testing email with random content to', dest_address)
    if len(attached) > 0:
        print('>>> attaching the file', attached)
    subject = 'Send email test {}'.format(randint(100, 999))
    msg = 'Hello Gmail at {}.'.format(datetime.now())
    refused = send_mail(dest_address, subject, msg, attachment=attached)
    if len(refused) > 0:
        print('>>>>>>>> The recipient was refused')
        print(refused)
    else:
        print('>>>>>>>> Done!')


if __name__ == "__main__":
    main(sys.argv)
