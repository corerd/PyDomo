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


class Client(object):
    def __init__(self, ip):
        self.ip = ip
        self.attempt_cnt = 0
        self.last_attempt_timestamp = 0
        self.end_of_timedelay = 0

    def is_waiting(self):
        '''Returns the delay status'''
        if self.end_of_timedelay > time():
            # client is still waiting
            return True
        return False


class BruteForceAttackers(object):
    '''Prevent large numbers of rapid-fire successive login attempts
    (ie. the brute force attack).

    Following the guidelines in http://stackoverflow.com/a/477578
    perform login throttling: that is, set a time delay between attempts
    after N failed attempts.

    During the above time interval, login attempts from a specific IP address
    should not be accepted or evaluated at all.
    That is, correct credentials will not return in a successful login,
    and incorrect credentials will not trigger a delay increase.
    '''
    TIME_DELAY = 900.0  # seconds = 15 minutes
    MAX_FAILED_ATTEMPTS = 4  # time delay effects only when reach this number

    def __init__(self):
        self.clnt_blacklist = {}

    def remove(self, client_ip):
        try:
            del self.clnt_blacklist[client_ip]
        except KeyError:
            # client not found
            return

    def append(self, client_ip, time_delay=TIME_DELAY):
        '''If not found then create an instance of the client identified by IP
        and append it to the black list.
        Then set a time delay between attempts after MAX_FAILED_ATTEMPTS.

        Returns the client.
        '''
        client = None
        try:
            client = self.clnt_blacklist[client_ip]
        except KeyError:
            # client not found
            client = Client(client_ip)
            self.clnt_blacklist[client_ip] = client
        client.attempt_cnt = client.attempt_cnt + 1
        client.last_attempt_timestamp = time()
        client.end_of_timedelay = client.last_attempt_timestamp
        if client.attempt_cnt > self.MAX_FAILED_ATTEMPTS:
            client.end_of_timedelay = client.end_of_timedelay + time_delay
        return client


def test_bench():
    TB_TIME_DELAY = 5
    from time import sleep

    print('Start Test Bench')
    ip_list = ['0.0.0.1', '0.0.0.2', '0.0.0.3']
    attacker = BruteForceAttackers()
    for ip in ip_list:
        print('Add client IP %s in black list (%d attempts)' %
                                        (ip, attacker.MAX_FAILED_ATTEMPTS + 1))
        for attempt in range(attacker.MAX_FAILED_ATTEMPTS):
            if attacker.append(ip, TB_TIME_DELAY).is_waiting() is True:
                print('FAIL: time delay goes on at %d attempt' % (attempt + 1))
        if attacker.append(ip, TB_TIME_DELAY).is_waiting() is not True:
            print("FAIL: time delay doesn't go on after %d attempt" %
                                                attacker.MAX_FAILED_ATTEMPTS)
        sleep(0.5)

    print('Check timeout')
    start_wait = time()
    waiting_list = {ip: True for ip in ip_list}
    some_is_waiting = True
    while some_is_waiting:
        delta = time() - start_wait
        if delta > TB_TIME_DELAY * len(ip_list):
            print('FAIL: %fs exceed delta time' % delta)
            break
        some_is_waiting = False
        for client in list(waiting_list.keys()):
            try:
                waiting_list[client] = \
                                attacker.clnt_blacklist[client].is_waiting()
            except KeyError:
                # client not found
                waiting_list[client] = False
            if waiting_list[client] is True:
                some_is_waiting = True
        sleep(0.1)

    print('Leave Test Bench')


if __name__ == '__main__':
    test_bench()
