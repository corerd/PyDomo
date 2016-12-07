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

from __future__ import print_function

import json
from time import time, localtime
from os.path import join

from cloud.weather import DEFAULT_CFG_FILE_PATH, getLocationTemp
from cloud.cloudcfg import ConfigDataLoad


DEFAULT_BOILERSTATUS = \
{
    'power': 'OFF',
    'power-on-time': '0'
}
BOILERSTATUS_FILE = 'boilerstatus.json'
POWER_ON_DURATION = 1*60*60  # 1 hour as seconds keeping power ON
POWER_ON_INTERVAL = 6*60*60  # 6 hours as seconds between two successive starts
EARLY_MORNING_HOURS = range(5, 8)  # that is 5, 6, 7
ICE_ALERT_THRESHOLD = 4.0  # Celsius degrees


def isTimeToPowerOn(weatherSrvCfg):
    """ Check the external temperature against an ice alert threshold.
    The temperature is get from a cloud service.
    If the cloud service is not available,
    then power on at least once a day.
    """
    locationTemp = getLocationTemp( weatherSrvCfg['wu-api-key'],
                                    weatherSrvCfg['wu-search-country'],
                                    weatherSrvCfg['wu-search-city'] )
    if len(locationTemp) <= 0:
        # cloud service is not available,
        # check early morning time.
        current_hour = localtime()[3]
        return current_hour in EARLY_MORNING_HOURS
    c_temp = locationTemp[1]
    if c_temp > ICE_ALERT_THRESHOLD:
        return False
    return True


def crank(cfg):
    boilerstatus_file = join(cfg.data['datastore'], BOILERSTATUS_FILE)
    boilerstatus = ConfigDataLoad(boilerstatus_file, DEFAULT_BOILERSTATUS)
    current_time = int(time())

    if boilerstatus.data['power'] == 'ON':
        if current_time - boilerstatus.data['power-on-time'] >= POWER_ON_DURATION:
            boilerPowerOff()
            boilerstatus.data['power'] = 'OFF'
            boilerstatus.update()
    else:
        # boiler power is OFF
        if current_time - boilerstatus.data['power-on-time'] >= POWER_ON_INTERVAL:
            if isTimeToPowerOn(cfg.data):
                boilerPowerOn()
                boilerstatus.data['power'] = 'ON'
                boilerstatus.data['power-on-time'] = current_time
                boilerstatus.update()


def main():
    try:
        cfg = ConfigDataLoad(DEFAULT_CFG_FILE_PATH)
    except:
        print('Unable to load config', file=sys.stderr)
        return -1
    crank(cfg)
    return 0


if __name__ == "__main__":
    exit(main())
