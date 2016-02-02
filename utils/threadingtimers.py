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
from time import sleep
from threading import Event, Thread


class ThreadingTimers(Thread):
    '''Create a reusable timer.
    A callback function will run after interval seconds have passed.
    '''
    def __init__(self, on_timeout):
        '''Callback function will run after interval seconds have passed'''
        super(ThreadingTimers, self).__init__(target=self.timer_run)
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

    def timer_run(self):
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
        sleep(0.1)  # wait a timer_run cycle to reset _f_timing

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
    '''ThreadingTimers Test Bench'''
    from time import time
    import logging

    logging.basicConfig(level=logging.DEBUG,
                        format='(%(threadName)-9s) %(message)s',)

    class UT_ThreadingTimers(object):
        '''Unit test for ThreadingTimers class'''
        def __init__(self, timer_name):
            self.start_time = 0
            self.interval_time = 0
            self.timer = ThreadingTimers(self.on_timeout)
            self.timer.setName(timer_name)
            logging.debug('Unit Test for %s has been created' %
                                                        self.timer.getName())

        def on_timeout(self):
            delta = time() - self.start_time
            logging.debug('compare elapesed %fs with given %fs time' %
                                                (delta, self.interval_time))
            if delta < self.interval_time:
                logging.debug('FAIL: terminated prematurely')
            else:
                logging.debug('done!')

        def start_timer(self, interval):
            '''Wait an interval of time'''
            self.interval_time = interval
            self.start_time = time()
            self.timer.start(interval)

        def timer_wait(self, interval):
            '''Wait an interval of time.
            The time elapsed must match.
            '''
            logging.debug('waiting %s for %fs' %
                                        (self.timer.getName(), interval))
            self.start_timer(interval)
            while self.timer.is_timing():
                sleep(0.1)
            now = time()
            if now - self.start_time < interval:
                logging.debug('%s FAIL' % self.timer.getName())
                return 1
            return 0

        def timer_wait_after_restart(self, interval, interval_reloaded):
            '''Start a timer interval and suddenly reload with new one
            before the first expired.
            The time elapsed must match.
            '''
            logging.debug('Reload %s with %fs after %fs' %
                        (self.timer.getName(), interval_reloaded, interval))
            self.start_timer(interval)
            self.start_timer(interval_reloaded)
            while self.timer.is_timing():
                sleep(0.1)
            now = time()
            if now - self.start_time < interval_reloaded:
                logging.debug('%s FAIL' % self.timer.getName())
                return 1
            return 0

        def timer_cancel(self, interval):
            '''Start and subsequently cancel a timer.
            Check is_timing method returning the timer status accordingly.
            '''
            logging.debug('Check %s running status' % self.timer.getName())
            if self.timer.is_timing():
                self.timer.cancel()
            if self.timer.is_timing():
                logging.debug('FAIL: cannot stop %s' % self.timer.getName())
                return 1
            logging.debug('Try to stop %s before %fs' %
                                            (self.timer.getName(), interval))
            self.start_timer(interval)
            if self.timer.is_timing() is not True:
                logging.debug('FAIL: cannot start %s' % self.timer.getName())
                return 1
            self.timer.cancel()
            if self.timer.is_timing():
                logging.debug('FAIL: cannot cancel %s' % self.timer.getName())
                return 1
            delta_time = time() - self.start_time
            if delta_time > 0.5:
                logging.debug('FAIL: %s delta time %fs' %
                                            (self.timer.getName(), delta_time))
                return 1
            logging.debug('DONE: %s' % self.timer.getName())
            return 0

        def finish(self):
            '''Kill the timer thread.
            '''
            logging.debug('Terminating %s...' % self.timer.getName())
            now = time()
            self.timer.terminate(True)
            delta = time() - now
            logging.debug('%s delta = %fs' % (self.timer.getName(), delta))
            if delta > 0.2:
                '''The timer should not be running because of the testing flow.
                Anyway accept a small delay in slow systems.
                '''
                logging.debug('FAIL: %s should not be pending' %
                                                        self.timer.getName())
                return 1
            return 0

    ''' TEST BENCH '''
    logging.debug('--- TEST BENCH RUNNING ---')
    tb_timer1 = UT_ThreadingTimers('Timer1')
    tb_timer2 = UT_ThreadingTimers('Timer2')
    error_cnt = 0
    ut_cnt = 0
    for cnr in range(2):
        ut_cnt = ut_cnt + 1
        error_cnt = error_cnt + tb_timer1.timer_wait(3)
        ut_cnt = ut_cnt + 1
        error_cnt = error_cnt + tb_timer2.timer_wait(3)
        ut_cnt = ut_cnt + 1
        error_cnt = error_cnt + tb_timer1.timer_wait_after_restart(3, 5)
        ut_cnt = ut_cnt + 1
        error_cnt = error_cnt + tb_timer2.timer_wait_after_restart(3, 5)
        ut_cnt = ut_cnt + 1
        error_cnt = error_cnt + tb_timer1.timer_cancel(3)
        ut_cnt = ut_cnt + 1
        error_cnt = error_cnt + tb_timer2.timer_cancel(3)
        ut_cnt = ut_cnt + 1
        error_cnt = error_cnt + tb_timer1.timer_wait(2)
        ut_cnt = ut_cnt + 1
        error_cnt = error_cnt + tb_timer2.timer_wait(2)
        ut_cnt = ut_cnt + 1
        error_cnt = error_cnt + tb_timer1.timer_cancel(2)
        ut_cnt = ut_cnt + 1
        error_cnt = error_cnt + tb_timer2.timer_cancel(2)
        ut_cnt = ut_cnt + 1
        error_cnt = error_cnt + tb_timer1.timer_wait_after_restart(2, 4)
        ut_cnt = ut_cnt + 1
        error_cnt = error_cnt + tb_timer2.timer_wait_after_restart(2, 4)
        ut_cnt = ut_cnt + 1
        error_cnt = error_cnt + tb_timer1.timer_wait_after_restart(5, 2)
        ut_cnt = ut_cnt + 1
        error_cnt = error_cnt + tb_timer2.timer_wait(1)
        ut_cnt = ut_cnt + 1
        error_cnt = error_cnt + tb_timer1.timer_wait(1)
        ut_cnt = ut_cnt + 1
        error_cnt = error_cnt + tb_timer2.timer_cancel(1)
        ut_cnt = ut_cnt + 1
        error_cnt = error_cnt + tb_timer1.timer_cancel(4)
        ut_cnt = ut_cnt + 1
        error_cnt = error_cnt + tb_timer2.timer_cancel(4)
        ut_cnt = ut_cnt + 1
        error_cnt = error_cnt + tb_timer1.timer_cancel(1)
        ut_cnt = ut_cnt + 1
        error_cnt = error_cnt + tb_timer2.timer_wait_after_restart(1, 3)
        ut_cnt = ut_cnt + 1
        error_cnt = error_cnt + tb_timer1.timer_wait(4)
        ut_cnt = ut_cnt + 1
        error_cnt = error_cnt + tb_timer2.timer_wait(4)
        ut_cnt = ut_cnt + 1
        error_cnt = error_cnt + tb_timer1.timer_wait_after_restart(1, 3)
        ut_cnt = ut_cnt + 1
        error_cnt = error_cnt + tb_timer2.timer_wait_after_restart(5, 2)

    ut_cnt = ut_cnt + 1
    error_cnt = error_cnt + tb_timer1.finish()
    ut_cnt = ut_cnt + 1
    error_cnt = error_cnt + tb_timer2.finish()
    logging.debug('--- Finished with %d/%d errors ---' % (error_cnt, ut_cnt))
