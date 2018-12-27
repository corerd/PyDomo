#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''Dark Sky Weather API wrapper
Link: https://darksky.net/dev
'''
from __future__ import print_function

from sys import argv as cmd_args
import urllib2
import json
import time
import sys


def print_error(msg):
    print('%s;%s' % (time.strftime("%Y-%m-%d %H:%M:%S"), msg), file=sys.stderr)


def getCurrentTemp(user_api_key, latitude, longitude):
    """Get current temperature in Celsius degrees from Dark Sky API weather data.
    API doc: https://darksky.net/dev/docs

    Return tuple (city, temperature, nearest_station), empty tuple if rised some errors.
    """
    #request_url = 'https://api.darksky.net/forecast/%s/%s,%s?units=si&exclude=minutely,hourly,daily,alerts,flags' % \
    request_url = 'https://api.darksky.net/forecast/%s/%s,%s?units=si&exclude=minutely,hourly,daily,alerts' % \
                                                ( user_api_key, latitude, longitude )
    try:
        f = urllib2.urlopen(request_url)
        json_string = f.read()
        f.close()
    except:
        # See: http://stackoverflow.com/a/4990739
        print_error("DSA: urllib2 error;%s" % sys.exc_info()[0])
        return ()
    try:
        parsed_json = json.loads(json_string)
        location = parsed_json['timezone']
        temp_c = parsed_json['currently']['temperature']
        nearest_station = parsed_json['flags']['nearest-station']
    except:
        # See: http://stackoverflow.com/a/4990739
        #print(json_string, file=sys.stderr)
        print_error("DSA: parse json error;%s" % sys.exc_info()[0])
        return ()
    try:
        f_temp_c = float(temp_c)
    except:
        # See: http://stackoverflow.com/a/4990739
        print_error("DSA: string convertion to float error;%s" % sys.exc_info()[0])
        return ()
    return (location, f_temp_c, nearest_station)


def main(argv):
    print('Dark Sky API: get the temperature of the provided location.')
    if len(argv) != 4:
        print('SINTAX: %s <api-key> <location-latitude> <location-longitude>' % argv[0])
        return -1
    api_key = argv[1]
    latitude = argv[2]
    longitude = argv[3]
    locationTemp = getCurrentTemp(api_key, latitude, longitude)
    if len(locationTemp) == 0:
        print('Weather service is not available')
        return -1
    print('Temperature is %d* C (timezone %s)' % (locationTemp[1], locationTemp[0]))
    print('Nearest station: %s km' % locationTemp[2])
    return 0


if __name__ == "__main__":
    exit(main(cmd_args))
