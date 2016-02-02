#!/usr/bin/env python
#
# The MIT License (MIT)
#
# Copyright (c) 2016 Corrado Ubezio
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

'''Website authentication

Follow the guidelines in http://stackoverflow.com/a/477578
'''

from __future__ import print_function
from time import time
from utils.threadingtimers import ThreadingTimers


class Client(object):
    MAX_FAILED_ATTEMPTS = 1  # time delay goes into effect after these
    TIME_DELAY = 3  # seconds

    def __init__(self, ip):
        self.ip = ip
        self.login_tries = 0
        self.login_delay_expired_timestamp = 0
        self.login_delay = ThreadingTimers(self.on_timeout)
        self.login_delay.setName(self.ip)

    def on_timeout(self):
        '''Record the time'''
        self.login_delay_expired_timestamp = time()


class Authenticator(object):

    def __init__(self):
        self.clnt_blacklist = {}

    def authorize(self, user, password):
        pass

    def blist_add(self, client_ip):
        client = Client(client_ip)
        self.clnt_blacklist[client_ip] = client

    def blist_remove(self, client_ip):
        try:
            self.clnt_blacklist[client_ip].login_delay.terminate()
            del self.clnt_blacklist[client_ip]
        except KeyError:
            # not found
            pass

    def blist_search(self, client_ip):
        '''Returns the matching client (None otherwise)'''
        client = None
        try:
            client = self.clnt_blacklist[client_ip]
        except KeyError:
            # not found
            pass
        return client

    def add_delay(self, client_ip):
        client = None
        try:
            client = self.clnt_blacklist[client_ip]
        except KeyError:
            # if not found then add a new client in black list
            client = Client(client_ip)
            self.clnt_blacklist[client_ip] = client
        client.login_tries = client.login_tries + 1
        if client.login_tries >= client.MAX_FAILED_ATTEMPTS:
            client.login_delay.start(client.TIME_DELAY)

    def is_login_delaying(self, client_ip):
        '''Returns login delay status'''
        client = None
        try:
            client = self.clnt_blacklist[client_ip]
        except KeyError:
            # if not found in black list then it is not delaying
            return False
        return client.login_delay.is_timing()


def test_bench():
    auth = Authenticator()
    auth.blist_add('0.0.0.1')
    auth.blist_add('0.0.0.2')
    auth.blist_add('0.0.0.3')
    auth.blist_add('0.0.0.4')
    print(auth.clnt_blacklist)
    for client_search in auth.clnt_blacklist:
        print('%s : %s' % (client_search, auth.blist_search(client_search)))


if __name__ == '__main__':
    pass