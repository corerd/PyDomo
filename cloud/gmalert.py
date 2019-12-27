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
import time
import json
from sys import stderr
from time import strftime
from os import mkdir
from os.path import dirname, join, isdir, realpath

from apiclient import errors
from traceback import format_exc

from cloud.cloudcfg import ConfigDataLoad, checkDatastore
from googleapis.gmailapi import gmSend


# Globals
VERSION = '1.0'
VERSION_DATE = '2019'
DEFAULT_CFG_FILE = 'cloudcfg.json'
LOG_FILE = 'gmalert-log.txt'

DEFAULT_CFG_FILE_PATH = join(dirname(realpath(__file__)), DEFAULT_CFG_FILE)

USAGE = '''Send an email alert message from the user's Gmail account.

Data are logged in CSV format: datetime;city;temperature

Email address of the receiver and datastore path are taken from a configuration
file in JSON format.
If none is given, the configuration is read from the file:
    %s
''' % DEFAULT_CFG_FILE_PATH


def print_error(msg):
    print('%s;%s' % (strftime("%Y-%m-%d %H:%M:%S"), msg), file=stderr)


def alert_send(subject, message_text):
    """Send an alert email message from the user's account
    to the email address get from the configuration file.

    Args:
        subject: The subject of the email message.
        message_text: The text of the email message.

    Returns:
        Success.
    """
    # get the configuration file
    try:
        cloud_cfg = ConfigDataLoad(DEFAULT_CFG_FILE_PATH)
    except Exception as e:
        print_error('cloud configuration: unable to load %s' % DEFAULT_CFG_FILE_PATH)
        print_error('cloud configuration exception: %s' % type(e).__name__)
        print_error('cloud configuration: %s' % str(e))
        return -1

    # logger setup
    log_file = join(cloud_cfg.data['datastore'], LOG_FILE)
    if checkDatastore(log_file) is not True:
        print_error("Cannot access %s directory" % cloud_cfg.data['datastore'])
        return -1
    logging.basicConfig(filename=log_file,
                        format='%(asctime)s;%(levelname)s;%(message)s',
                        level=logging.DEBUG)

    # send the alert message
    try:
        receiver_address = cloud_cfg.data['alert-receiver-address']
    except KeyError:
        logging.error("Keyword 'alert-receiver-address' not found in file %s" %
                        DEFAULT_CFG_FILE_PATH)
        return -1

    success = -1
    try:
        gmSend(receiver_address, subject, message_text)
    except errors.HttpError as e:
        logging.error('HttpError occurred: %s' % e)
    except Exception:
        logging.error(format_exc())
    else:
        logging.info(message_text)
        success = 0

    return success


if __name__ == "__main__":
    pass
