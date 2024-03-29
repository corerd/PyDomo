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

import logging
import time
import json
import sys
from os.path import dirname, join, realpath

try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen


# Globals
VERSION = '2.0'
VERSION_DATE = '2016-18'
DEFAULT_CFG_FILE = 'cloudcfg.json'

DEFAULT_CFG_FILE_PATH = join(dirname(realpath(__file__)), DEFAULT_CFG_FILE)

USAGE = '''Get the location current temperature in Celsius degrees.

Data are logged in CSV format: datetime;city;temperature

Location and datastore path are taken from a configuration file in JSON format.
If none given, the configuration is read from the file:
    %s
''' % DEFAULT_CFG_FILE_PATH


def print_error(msg):
    print('%s;%s' % (time.strftime("%Y-%m-%d %H:%M:%S"), msg), file=sys.stderr)


def getJsonItemByPath(nested_json_value, path_to_field):
    """Return the value of nested field in JSON object.
    path_to_field is a string consisting of individual keys separated by '/'.
    If the JSON object contains arrays, the key is its numeric index.
    """
    for key in path_to_field.split("/"):
        if key.isdigit():
            # Accessing array
            nested_json_value = nested_json_value[int(key)]
        else:
            nested_json_value = nested_json_value.get(key)
    return nested_json_value


def getLocationTempFromSvc(svc_api, search_lat, search_lon, search_name):
    """Use a weather service api to get the current temperature
    by location coordinates latitude and longitude.
    'search_name' is used only if the api doesn't return the location name.

    Returns tuple (location_name, temperature-celsius-degrees),
    otherwise an empty tuple if rised some errors.
    """
    request_url = svc_api['request'].format( key=svc_api['key'],
                                             lat=search_lat, lon=search_lon )
    try:
        f = urlopen(request_url)
        json_string = f.read()
        f.close()
    except:
        # See: http://stackoverflow.com/a/4990739
        print_error("%s: urllib2 error;%s" % (svc_api['name'], sys.exc_info()[0]))
        return ()
    try:
        # Parse the JSON object
        json_obj = json.loads(json_string)
        temp_c = getJsonItemByPath(json_obj, svc_api['path-to-temperature-value'])
    except:
        # See: http://stackoverflow.com/a/4990739
        #print(json_string, file=sys.stderr)
        print_error("%s: parse json error;%s" % (svc_api['name'], sys.exc_info()[0]))
        return ()
    try:
        f_temp_c = float(temp_c)
    except:
        # See: http://stackoverflow.com/a/4990739
        print_error("%s: string convertion to float error;%s" % (svc_api['name'], sys.exc_info()[0]))
        return ()
    try:
        location_name = getJsonItemByPath(json_obj, svc_api['optional-path-to-city-name'])
    except:
        # API doesn't return the location name
        # then use the provided one
        location_name = search_name
    return (location_name, f_temp_c)


def updateLogFromSvcs(weatherSvc):
    """Updates location temperature log from a bunch of weather services.
    Log CSV format: datetime;api-name;city;temperature
    If getting the temperature fron a service doesn't succeed,
    then 'city' and 'temperature' fields are replaced by '-'.
    Return value is always 0
    """
    location_name = weatherSvc['location']['name']
    latitude = weatherSvc['location']['lat']
    longitude = weatherSvc['location']['lon']
    for api in weatherSvc['api-list']:
        locationTemp = getLocationTempFromSvc(api, latitude, longitude, location_name)
        if len(locationTemp) <= 0:
            # error
            logging.info("%s;-;-" % api['name'])
        else:
            logging.info("%s;%s;%0.1f" % (api['name'], locationTemp[0], locationTemp[1]))
    return 0


def main():
    from utils.cli import cfg_file_arg
    from cloudcfg import ConfigDataLoad, checkDatastore

    options = cfg_file_arg(VERSION, USAGE, DEFAULT_CFG_FILE_PATH, VERSION_DATE)
    print('Read configuration from file: %s' % options.cfg_file)

    try:
        cfg = ConfigDataLoad(options.cfg_file)
    except:
        print_error('Unable to load config')
        return -1

    log_file = join(cfg.data['datastore'], "temperature.txt")
    if checkDatastore(log_file) is not True:
        print_error("Cannot access %s directory" % cfg.data['datastore'])
        return -1

    logging.basicConfig(filename=log_file,
                        format='%(asctime)s;%(levelname)s;%(message)s',
                        level=logging.DEBUG)

    # OLD getLocationTemp from Wunderground only service
    #status = updateLog( cfg.data['wu-api-key'],
    #                    cfg.data['wu-search-country'],
    #                    cfg.data['wu-search-city'] )

    # NEW getLocationTemp from a bunch of weather services
    status = updateLogFromSvcs( cfg.data['weather-svc'] )
    if status == 0:
        print('Temperature log in file: %s' % log_file)
    else:
        print_error('FAIL!')
    return status


if __name__ == "__main__":
    exit(main())
