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
import urllib2
import json
import sys
from os import mkdir
from os.path import dirname, join, isdir, realpath


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


def getDicItemByPath(dic, path_to_value):
    key_list = path_to_value.split('/')
    for key in key_list[:-1]:
        dic = dic[key]
    key = key_list[-1]
    return dic[key]


def getLocationTempFromSvc(svc_api, search_lat, search_lon):
    """NEW Use a weather service api to get the current temperature
    by location coordinates latitude and longitude.
    'search_name' is used only if the api don't return the city name.

    Returns tuple (city, temperature-celsius-degrees),
    otherwise an empty tuple if rised some errors.
    """
    request_url = svc_api['request'].format( key=svc_api['key'],
                                             lat=search_lat, lon=search_lon )
    try:
        f = urllib2.urlopen(request_url)
        json_string = f.read()
        f.close()
    except:
        # See: http://stackoverflow.com/a/4990739
        print_error("%s: urllib2 error;%s" % (svc_api['name'], sys.exc_info()[0]))
        return ()
    try:
        parsed_json = json.loads(json_string)
        temp_c = getDicItemByPath(parsed_json, svc_api['path-to-temperature-value'])
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
        location = getDicItemByPath(parsed_json, svc_api['optional-path-to-city-name'])
    except:
        location = '<default>'
    return (location, f_temp_c)


def updateLogFromSvcs(weatherSvc):
    """Updates location temperature log from a bunch of weather services.
    Log CSV format: datetime;api-name;city;temperature
    If getting the temperature fron a service doesn't succeed,
    then 'city' and 'temperature' fields are replaced by '-'.
    Return value is always 0
    """
    latitude = weatherSvc['location']['lat']
    longitude = weatherSvc['location']['lon']
    for api in weatherSvc['api-list']:
        locationTemp = getLocationTempFromSvc(api, latitude, longitude)
        if len(locationTemp) <= 0:
            # error
            logging.info("%s;-;-" % api['name'])
        else:
            logging.info("%s;%s;%0.1f" % (api['name'], locationTemp[0], locationTemp[1]))
    return 0


### BEGIN OF OLD getLocationTemp from Wunderground only service ###

def wu_getConditions(user_api_key, country, city):
    """Get the current temperature in Celsius degrees using Weather Underground API.
    Weather Underground home: "https://www.wunderground.com/weather/api

    Return tuple (city, temperature), empty tuple if rised some errors.
    """
    wu_request_url = 'http://api.wunderground.com/api/%s/geolookup/conditions/q/%s/%s.json' % \
                                                ( user_api_key, country, city )
    try:
        f = urllib2.urlopen(wu_request_url)
        json_string = f.read()
        f.close()
    except:
        # See: http://stackoverflow.com/a/4990739
        print_error("WU: urllib2 error;%s" % sys.exc_info()[0])
        return ()
    try:
        parsed_json = json.loads(json_string)
        location = parsed_json['location']['city']
        temp_c = parsed_json['current_observation']['temp_c']
    except:
        # See: http://stackoverflow.com/a/4990739
        #print(json_string, file=sys.stderr)
        print_error("WU: parse json error;%s" % sys.exc_info()[0])
        return ()
    try:
        f_temp_c = float(temp_c)
    except:
        # See: http://stackoverflow.com/a/4990739
        print_error("WU: string convertion to float error;%s" % sys.exc_info()[0])
        return ()
    return (location, f_temp_c)


def getLocationTemp(user_api_key, country, city):
    """Return tuple (city, temperature), empty tuple if rised some errors.
    """
    retries = 0
    locationTemp = wu_getConditions(user_api_key, country, city)
    while len(locationTemp) <= 0:
        if retries >= 2:
            break
        retries = retries + 1
        time.sleep(10)
        locationTemp = wu_getConditions(user_api_key, country, city)
    return locationTemp


def updateLog(user_api_key, country, city):
    """Updates location temperature log in CSV format: datetime;city;temperature
    Return value is 0 for SUCCESS, -1 otherwise
    """
    locationTemp = getLocationTemp(user_api_key, country, city)
    if len(locationTemp) <= 0:
        logging.error("getLocationTemp")
        return -1
    logging.info("%s;%0.1f" % (locationTemp[0], locationTemp[1]))
    return 0

### END OF OLD getLocationTemp from Wunderground only service ###


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
