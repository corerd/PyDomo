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

'''Timer with threads

The timer instance of the built-in threading.Timer class is not reusable
after an interval of time has passed.

This module defines a subclass of threading.Thread in order to create
a single thread to handle a reusable timer.
It is also defined an action to run after the interval of time has passed.

References:
http://stackoverflow.com/a/5205180
http://stackoverflow.com/a/9812806
http://stackoverflow.com/a/5205180
http://www.bogotobogo.com/python/Multithread/python_multithreading_subclassing_Timer_Object.php
'''

from __future__ import print_function
from threading import Event, Thread


class ThreadingTimers(Thread):
    '''Create a reusable timer.
    A callback function will run after interval seconds have passed.
    '''
    def __init__(self, on_timeout):
        '''Callback function will run after interval seconds have passed'''
        super(ThreadingTimers, self).__init__()
        self.interval = 0
        self.cbk_ontimeout = on_timeout
        self.run_evt = Event()
        self.stop_evt = Event()
        self._f_running = False
        self._f_timing = False

    def start(self, interval):
        '''Overrides Thread start method.
        Start the timer till interval seconds have passed.
        If a timer is already running, stop and restart with the new interval.
        '''
        if self.is_alive() is not True:
            self._f_running = True
            super(ThreadingTimers, self).start()
        if self.is_timing() is True:
            self.cancel()
        self.interval = interval
        self._f_timing = True
        self.run_evt.set()

    def run(self):
        while self._f_running is True:
            self.run_evt.wait()
            if self._f_running is not True:
                break
            self.run_evt.clear()
            self.stop_evt.wait(self.interval)
            if self.stop_evt.is_set() is not True:
                self.cbk_ontimeout()
            self.stop_evt.clear()
            self._f_timing = False

    def is_timing(self):
        '''Retus True is the timer is running'''
        return self._f_timing

    def cancel(self):
        '''Stop the timer, cancel the execution of the timer's action.'''
        self.stop_evt.set()

    def terminate(self, timeout=False):
        '''Kill and wait until the thread terminates.
        if 'timeout' then wait untill interval seconds have passed.
        '''
        self._f_running = False
        if timeout is not True:
            self.cancel()
        self.run_evt.set()
        self.join()


if __name__ == '__main__':
    '''ThreadingTimers Class Demo'''
    import time
    import logging

    logging.basicConfig(level=logging.DEBUG,
                        format='(%(threadName)-9s) %(message)s',)

    def time_spent():
        logging.debug('done waiting timer')

    t1 = ThreadingTimers(time_spent)
    t1.setName('t1')
    t2 = ThreadingTimers(time_spent)
    t2.setName('t2')

    logging.debug('starting timers...')

    t1.start(5)
    t2.start(20)
    logging.debug('waiting before canceling %s', t2.getName())
    time.sleep(2)
    logging.debug('canceling %s', t2.getName())
    print('before cancel t2.is_timing() = ', t2.is_timing())
    t2.cancel()
    time.sleep(2)
    print('after cancel t2.is_timing() = ', t2.is_timing())
    print('wait t1')
    while t1.is_timing():
        time.sleep(0.5)

    logging.debug('restarting timer1...')
    t1.start(3)
    print('wait t1')
    while t1.is_timing():
        time.sleep(0.5)

    logging.debug('restarting timer1 again...')
    t1.start(4)
    time.sleep(3)
    t1.start(10)
    print('wait t1')
    while t1.is_timing():
        time.sleep(0.5)

    logging.debug('terninating...')
    t1.terminate(True)
    t2.terminate(True)
    logging.debug('done')
