#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''Weather Underground Weather API wrapper
Link: https://www.wunderground.com
'''
from __future__ import print_function

from sys import argv as cmd_args
import urllib2
import json
import time
import sys


def print_error(msg):
    print('%s;%s' % (time.strftime("%Y-%m-%d %H:%M:%S"), msg), file=sys.stderr)


def getNearestStation(station_list):
    lowest_distance = float('inf')
    for station in station_list:
        distance = float(station['distance_km'])
        if lowest_distance > distance:
            lowest_distance = distance
    return len(station_list), lowest_distance


def getCurrentTemp(user_api_key, search_lat, search_lon):
    """Get current temperature in Celsius degrees from OpenWeatherMap weather data.
    API doc: https://www.wunderground.com/weather/api/d/docs

    Return tuple (city, temperature, nstations, nearest_station), empty tuple if rised some errors.
    """
    request_url = 'http://api.wunderground.com/api/{key}/geolookup/conditions/q/{lat},{lon}.json'.format(
                            key=user_api_key, lat=search_lat, lon=search_lon )
    try:
        f = urllib2.urlopen(request_url)
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
    try:
        station_summary = getNearestStation(parsed_json['location']['nearby_weather_stations']['pws']['station'])
    except:
        print_error("WU: nearby_weather_stations decoding error;%s" % sys.exc_info()[0])
        return ()
    return (location, f_temp_c, station_summary[0], station_summary[1])


def main(argv):
    print('Wunderground: get the temperature of the provided city.')
    if len(argv) != 4:
        print('SINTAX: %s <api-key> <city-latitude> <city-longitude>' % argv[0])
        return -1
    api_key = argv[1]
    latitude = argv[2]
    longitude = argv[3]
    locationTemp = getCurrentTemp(api_key, latitude, longitude)
    if len(locationTemp) == 0:
        print('Weather service is not available')
        return -1
    print('Temperature of "%s" is %d* C' % (locationTemp[0], locationTemp[1]))
    print('Nearby weather station on %d is at %s km' % (locationTemp[2], locationTemp[3]))
    return 0


if __name__ == "__main__":
    exit(main(cmd_args))
