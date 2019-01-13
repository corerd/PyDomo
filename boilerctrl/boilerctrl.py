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

"""Use cloud and camrecorder modules.
datastore path must be the same.
"""

from __future__ import print_function

import json
import logging
from sys import stderr
from os import devnull
from os.path import join
from subprocess import STDOUT, call
from time import time, localtime, sleep, strftime

from cloud.upload import upload_datastore
from cloud.cloudcfg import ConfigDataLoad, checkDatastore
from cloud.weather import DEFAULT_CFG_FILE_PATH as CLOUD_DEFUALT_PATH, getLocationTemp, getLocationTempFromSvc
from camrecorder.camsnapshot import DEFAULT_CFG_FILE_PATH as CAMRECORDER_DEFUALT_PATH, snap_shot


# Globals
VERSION = '1.0'
VERSION_DATE = '2016'

DEFAULT_BOILERSTATUS = \
{
    'power': 'OFF',
    'power-on-time': '0'
}
BOILERSTATUS_FILE = 'boilerstatus.json'
LOG_FILE = 'boilerctrl-log.txt'
POWER_ON_DURATION = 1*60*60  # 1 hour as seconds keeping power ON
POWER_OFF_INTERVAL = 5*60*60  # 4 hours as seconds between two successive starts
EARLY_MORNING_HOURS = range(5, 8)  # that is 5, 6, 7
ICE_ALERT_THRESHOLD = 2.0  # Celsius degrees


def print_error(msg):
    print('%s;%s' % (strftime("%Y-%m-%d %H:%M:%S"), msg), file=stderr)


def getExternalTempFromSvcs(weatherSvc):
    """Get the external temperature from a bunch of weather services.
    Returns the average temperature between the available services,
    None otherwise.
    """
    latitude = weatherSvc['location']['lat']
    longitude = weatherSvc['location']['lon']
    c_temp = 0
    nsvc = 0
    for api in weatherSvc['api-list']:
        locationTemp = getLocationTempFromSvc(api, latitude, longitude)
        if len(locationTemp) <= 0:
            # error: the weather service is not available
            logging.info("ext temp;%s;-" % api['name'])
        else:
            nsvc = nsvc + 1
            svc_temp = locationTemp[1]
            c_temp = c_temp + svc_temp
            logging.info("ext temp;%s;%0.1f" % (api['name'], svc_temp))
    if nsvc == 0:
        logging.error('no weather service is available')
        return None
    # compute, log and return average temperature
    c_temp = c_temp / nsvc
    logging.info("ext temp;%s;%0.1f" % ('AVERAGE', c_temp))
    return c_temp


def getExternalTemp(weatherSrvCfg):
    """OLD Get the external temperature from Wunderground service only.
    If the web service is not available, then returns None.
    """
    locationTemp = getLocationTemp( weatherSrvCfg['wu-api-key'],
                                    weatherSrvCfg['wu-search-country'],
                                    weatherSrvCfg['wu-search-city'] )
    if len(locationTemp) <= 0:
        logging.error('weather service is not available')
        return None
    c_temp = locationTemp[1]
    logging.info("ext temp;%0.1f" % c_temp)
    return c_temp


def isTimeToPowerOn(externalTemp):
    """ Check the external temperature against an ice alert threshold.
    If the external temperature is not available,
    check if currrent time is in early morning range
    so that the power is switched on at least once a day.
    """
    if externalTemp is None:
        # external temperature is not available,
        # check early morning time.
        current_hour = localtime()[3]
        isEarlyMorning = current_hour in EARLY_MORNING_HOURS
        if isEarlyMorning is True:
            logging.error('force switch ON at early morning')
        return isEarlyMorning
    if externalTemp > ICE_ALERT_THRESHOLD:
        return False
    return True


def boilerPowerSwitch(onOff):
    command = 'usbrelay UWMGH_1=%d' % onOff
    with open(devnull, 'w') as FNULL:
        call(command.split(), stdout=FNULL, stderr=STDOUT)


def boilerPowerOn(camrecorder_cfg):
    logging.info('boiler goes ON')
    snap_shot(camrecorder_cfg)  # take a snapshot before switching on
    boilerPowerSwitch(1)  # switch_on
    sleep(5)
    snap_shot(camrecorder_cfg)  # take a snapshot after switching on



def boilerPowerOff(camrecorder_cfg):
    logging.info('boiler goes OFF')
    snap_shot(camrecorder_cfg)  # take a snapshot before switching off
    boilerPowerSwitch(0)  # switch_off
    sleep(5)
    snap_shot(camrecorder_cfg)  # take a snapshot after switching off


def crank(cloud_cfg, camrecorder_cfg):
    log_file = join(cloud_cfg.data['datastore'], LOG_FILE)
    if checkDatastore(log_file) is not True:
        print_error("Cannot access %s directory" % cloud_cfg.data['datastore'])
        return -1
    logging.basicConfig(filename=log_file,
                        format='%(asctime)s;%(levelname)s;%(message)s',
                        level=logging.DEBUG)

    boilerstatus_file = join(cloud_cfg.data['datastore'], BOILERSTATUS_FILE)
    boilerstatus = ConfigDataLoad(boilerstatus_file, DEFAULT_BOILERSTATUS)
    boilerstatusChanged = False

    #OLD externalTemp = getExternalTemp(cloud_cfg.data)
    externalTemp = getExternalTempFromSvcs( cloud_cfg.data['weather-svc'] )

    current_time = int(time())
    try:
        power_on_time = int(boilerstatus.data['power-on-time'])
    except:
        logging.error('boiler status format')
        return

    if boilerstatus.data['power'] == 'ON':
        # Offset the initialization delays
        OFFSET_DELAY = 5*60  # 5 minutes as seconds
        if (current_time+OFFSET_DELAY) - power_on_time >= POWER_ON_DURATION:
            logging.debug('switch ON duration expired')
            boilerPowerOff(camrecorder_cfg)
            boilerstatus.data['power'] = 'OFF'
            boilerstatusChanged = True
    else:
        # boiler power is OFF
        if current_time - power_on_time >= POWER_OFF_INTERVAL:
            logging.debug('switch OFF duration expired')
            if isTimeToPowerOn(externalTemp):
                boilerPowerOn(camrecorder_cfg)
                boilerstatus.data['power'] = 'ON'
                boilerstatus.data['power-on-time'] = str(current_time)
                boilerstatusChanged = True

    if boilerstatusChanged is True:
        try:
            boilerstatus.update()
        except Exception as e:
            logging.error( '%s: %s' % (type(e).__name__, str(e)) )
        upload_datastore(cloud_cfg.data['datastore'])


def main():
    """Use cloud and camrecorder modules configuration files.
    datastore path must be the same.
    """
    print('boilerctrl v%s - (C) %s' % (VERSION, VERSION_DATE))

    try:
        cloud_cfg = ConfigDataLoad(CLOUD_DEFUALT_PATH)
    except Exception as e:
        print_error('cloud configuration: unable to load %s' % CLOUD_DEFUALT_PATH)
        print_error('cloud configuration exception: %s' % type(e).__name__)
        print_error('cloud configuration: %s' % str(e))
        return -1

    try:
        camrecorder_cfg = ConfigDataLoad(CAMRECORDER_DEFUALT_PATH)
    except Exception as e:
        print_error('camrecorder configuration: unable to load %s' % CAMRECORDER_DEFUALT_PATH)
        print_error('camrecorder configuration exception: %s' % type(e).__name__)
        print_error('camrecorder configuration: %s' % str(e))
        return -1

    crank(cloud_cfg, camrecorder_cfg)
    return 0


if __name__ == "__main__":
    exit(main())
