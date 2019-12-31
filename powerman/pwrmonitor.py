#!/usr/bin/env python
#
# The MIT License (MIT)
#
# Copyright (c) 2019 Corrado Ubezio
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

import logging
import json
import inspect
from sys import stderr
from time import strftime
from datetime import datetime
from os.path import dirname, join

from apiclient import errors
from traceback import format_exc

from powerman.upower import UPowerManager
from cloud.upload import upload_datastore
from cloud.googleapis.gmailapi import gmSend
from cloud.cloudcfg import ConfigDataLoad, checkDatastore

# Globals
VERSION = '1.0'
VERSION_DATE = '2019'

# Claud configuration file get from cloud package
DEFAULT_CFG_FILE = 'cloudcfg.json'
DEFAULT_CFG_FILE_PATH = join(dirname(inspect.getfile(ConfigDataLoad)),
                                DEFAULT_CFG_FILE)

# Power supply type IDs
PSU_UNKNOWN = -1
PSU_AC      = 0
PSU_BATTERY = 1

# Power supply type string description
PSU_AC_DESC      = "AC_ADAPTER"
PSU_BATTERY_DESC = "BATTERY"

# Files keeping power supply state
LOG_FILE = 'pwrmonitor-log.txt'
PSU_TYPE_FILE = 'pwrmonitor.json'
DEFAULT_PSU_CFG = \
{
    'power-supply': 'UNKNOWN'
}

USAGE = '''Check power supply type and if it is switched to battery
then send an email alert message from the user's Gmail account.

Data are logged in CSV format: datetime;city;temperature

Email address of the receiver and datastore path are taken from a configuration
file in JSON format.
If none is given, the configuration is read from the file:
    %s
''' % DEFAULT_CFG_FILE_PATH


def print_error(msg):
    print('%s;%s' % (strftime("%Y-%m-%d %H:%M:%S"), msg), file=stderr)


def psu_type_getFromCfg(cfg_data):
    """Get the power supply type from configuration data

    Args:
        cfg_data: PSU configuration data
    Returns:
        PSU_UNKNOWN
        PSU_AC
        PSU_BATTERY
    """
    psu_type_desc = cfg_data['power-supply']
    if psu_type_desc == PSU_BATTERY_DESC:
        return PSU_BATTERY
    elif psu_type_desc == PSU_AC_DESC:
        return PSU_AC
    return PSU_UNKNOWN


def psu_type_getFromDevice():
    """Get the power supply type from UPowerManager

    Returns:
        PSU_AC
        PSU_BATTERY
    """
    pwrMan = UPowerManager()
    # Get the Devices List searching for a battery
    battery_device = None
    for dev in pwrMan.detect_devices():
        if 'battery' in dev:
            battery_device = dev
            break
    if not battery_device:
        # no battery device found:
        #   power supply is external
        return PSU_AC
    if 'discharg' in pwrMan.get_state(battery_device).lower():
        # The battery power allowd states:
        #   "Unknown"
        #   "Loading" (that is Charging)
        #   "Discharging"
        #   "Empty"
        #   "Fully charged"
        #   "Pending charge"
        #   "Pending discharge"
        return PSU_BATTERY
    return PSU_AC


def alert_send(to, message_text):
    """Send an alert email message from the user's account
    to the email address get from the configuration file.

    Args:
        to: Email address of the receiver.
        message_text: The text of the alert message.

    Returns:
        Success.
    """
    subject = 'PSU Alert at ' + datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    success = -1
    try:
        gmSend(to, subject, message_text)
    except errors.HttpError as e:
        logging.error('HttpError occurred: %s' % e)
    except Exception:
        logging.error(format_exc())
    else:
        logging.info(message_text)
        success = 0
    return success


def main():
    print('pwrmonitor v%s - (C) %s' % (VERSION, VERSION_DATE))

    # get the configuration data
    try:
        cloud_cfg = ConfigDataLoad(DEFAULT_CFG_FILE_PATH)
    except Exception as e:
        print_error('cloud configuration: unable to load %s' % DEFAULT_CFG_FILE_PATH)
        print_error('cloud configuration exception: %s' % type(e).__name__)
        print_error('cloud configuration: %s' % str(e))
        return -1

    try:
        log_file = join(cloud_cfg.data['datastore'], LOG_FILE)
    except KeyError:
        print_error("Keyword 'datastore' not found in file %s" %
                        DEFAULT_CFG_FILE_PATH)
        return -1

    try:
        receiver_address = cloud_cfg.data['alert-receiver-address']
    except KeyError:
        print_error("Keyword 'alert-receiver-address' not found in file %s" %
                        DEFAULT_CFG_FILE_PATH)
        return -1

    # logger setup
    if checkDatastore(log_file) is not True:
        print_error("Cannot access %s directory" % cloud_cfg.data['datastore'])
        return -1
    logging.basicConfig(filename=log_file,
                        format='%(asctime)s;%(levelname)s;%(message)s',
                        level=logging.DEBUG)

    # check PSU type
    psu_switch2battery = 0
    psu_cfg_file = join(cloud_cfg.data['datastore'], PSU_TYPE_FILE)
    psu_cfg = ConfigDataLoad(psu_cfg_file, DEFAULT_PSU_CFG)
    psu_type_prev = psu_type_getFromCfg(psu_cfg.data)
    psu_type_current = psu_type_getFromDevice()
    if psu_type_current != psu_type_prev:
        if psu_type_current == PSU_BATTERY:
            psu_type_desc = PSU_BATTERY_DESC
        else:
            psu_type_desc = PSU_AC_DESC
        logging.info('power supply switched to {}'.format(psu_type_desc))
        psu_cfg.data['power-supply'] = psu_type_desc
        psu_cfg.update()
        if psu_type_current == PSU_BATTERY:
            psu_switch2battery = 1
            logging.debug('send alert')
            alert_send(receiver_address, 'AC power adapter has been unplugged.')
            upload_datastore(cloud_cfg.data['datastore'])

    return psu_switch2battery


if __name__ == "__main__":
    exit(main())
