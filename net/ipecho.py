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

'''IP releated stuff.
'''

from __future__ import print_function

import sys
import json
from re import sub
from requests import get

IPECHO_SERVICES_LIST_FILE = 'ipechosvc.jsn'


def search_from_service(url):
    '''Returns the public IP string from the service idientified by the url.
    If there are some communnication errors, returns an empty string.
    '''
    print("Service:", url, file=sys.stderr)
    try:
        r = get(url, timeout=10)
    except Exception:
        # TODO: better to handle exceptions as in:
        # http://docs.python-requests.org/en/latest/user/quickstart/#errors-and-exceptions
        return ''
    if r.status_code != 200:
        return ''
    # Returns the content of the server's response
    # after removing non-printable chars
    return sub('[^\040-\176]', '', r.text)


def get_my_public_ip():
    '''Returns the public IP string from the a pool of services.
    If there are some communnication errors, returns an empty string.
    '''
    my_ip = ''

    try:
        json_data = open(IPECHO_SERVICES_LIST_FILE)
        ipservices = json.load(json_data)
    except:
        print('Unable to load service list file:', IPECHO_SERVICES_LIST_FILE,
             file=sys.stderr)
        return my_ip
    json_data.close()

    for host in ipservices['host-list']:
        my_ip = search_from_service(host['url'])
        #print(">%s<" % my_ip, file=sys.stderr)
        if my_ip is not '':
            # Returns the first host response
            break
    return my_ip


if __name__ == "__main__":
    print('My IP is: >%s<' % get_my_public_ip())
