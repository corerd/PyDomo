#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''APIXU Weather API wrapper
Link: https://www.apixu.com/
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
    """Get current temperature in Celsius degrees from APIXU weather data.
    API doc: https://www.apixu.com/doc/

    Return tuple (city, temperature), empty tuple if rised some errors.
    """
    request_url = 'https://api.apixu.com/v1/current.json?key=%s&q=%s,%s' % \
                                                ( user_api_key, latitude, longitude )
    try:
        f = urllib2.urlopen(request_url)
        json_string = f.read()
        f.close()
    except:
        # See: http://stackoverflow.com/a/4990739
        print_error("APIXU: urllib2 error;%s" % sys.exc_info()[0])
        return ()
    try:
        parsed_json = json.loads(json_string)
        location = parsed_json['location']['name']
        temp_c = parsed_json['current']['temp_c']
    except:
        # See: http://stackoverflow.com/a/4990739
        #print(json_string, file=sys.stderr)
        print_error("APIXU: parse json error;%s" % sys.exc_info()[0])
        return ()
    try:
        f_temp_c = float(temp_c)
    except:
        # See: http://stackoverflow.com/a/4990739
        print_error("APIXU: string convertion to float error;%s" % sys.exc_info()[0])
        return ()
    return (location, f_temp_c)


def main(argv):
    print('APIXU: get the temperature of the provided location.')
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
    print('Temperature of "%s" is %d* C' % locationTemp)
    return 0


if __name__ == "__main__":
    exit(main(cmd_args))
