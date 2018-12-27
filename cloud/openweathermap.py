#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''OpenWeatherMap Weather API wrapper
Link: https://openweathermap.org/api
'''
from __future__ import print_function

from sys import argv as cmd_args
import urllib2
import json
import time
import sys


def print_error(msg):
    print('%s;%s' % (time.strftime("%Y-%m-%d %H:%M:%S"), msg), file=sys.stderr)


def getCurrentTemp(user_api_key, city_id):
    """Get current temperature in Celsius degrees from OpenWeatherMap weather data.
    API doc: https://openweathermap.org/current

    Return tuple (city, temperature), empty tuple if rised some errors.
    """
    request_url = 'http://api.openweathermap.org/data/2.5/weather?id=%s&units=metric&APPID=%s' % \
                                                ( city_id, user_api_key )
    try:
        f = urllib2.urlopen(request_url)
        json_string = f.read()
        f.close()
    except:
        # See: http://stackoverflow.com/a/4990739
        print_error("OWM: urllib2 error;%s" % sys.exc_info()[0])
        return ()
    try:
        parsed_json = json.loads(json_string)
        location = parsed_json['name']
        temp_c = parsed_json['main']['temp']
    except:
        # See: http://stackoverflow.com/a/4990739
        #print(json_string, file=sys.stderr)
        print_error("OWM: parse json error;%s" % sys.exc_info()[0])
        return ()
    try:
        f_temp_c = float(temp_c)
    except:
        # See: http://stackoverflow.com/a/4990739
        print_error("OWM: string convertion to float error;%s" % sys.exc_info()[0])
        return ()
    return (location, f_temp_c)


def getCityDesc(city_list, city_name):
    '''Returns a list of descriptors that match the searching 'city_name'
    in the 'city_list' json file.
    The list of cities is the city.list.json zipped file downloaded from
    http://bulk.openweathermap.org/sample/

    Each descriptor is represented as a dictionary with the following items:
    {
        "id": <city-id>,
        "name": <city-name>,
        "country": <country-code>,
        "coord": {
            "lon": <city-geo-location-longitude>,
            "lat": <city-geo-location-latitude>
        }
    }
    '''
    descList = []
    city_list_dict = json.loads(open(city_list).read())
    name = city_name.lower()
    for city_desc in city_list_dict:
        if city_desc['country'] == 'IT':
            name_found = city_desc['name'].lower()
            if name in name_found:
                descList.append(city_desc)
    return descList


def main(argv):
    print('OpenWeatherMap: get the temperature of the provided city.')
    if len(argv) != 4:
        print('SINTAX: %s <api-key> <city-list> <city-name>' % argv[0])
        return -1
    api_key = argv[1]
    city_list = argv[2]
    city_name = argv[3]
    print('Searching city ID of "%s" in %s ...' % (city_name, city_list))
    matches = getCityDesc(city_list, city_name)
    if len(matches) == 0:
        print('<city-name> not found!')
        return -1
    print('%d matches:' % len(matches))
    for city_desc in matches:
        print('ID %s: %s' % (city_desc['name'], city_desc['id']))
        coord = city_desc['coord']
        # Google Maps search by coordinates format
        print('Latitude and Longitude: %s, %s' % (coord['lat'], coord['lon']))
        locationTemp = getCurrentTemp(api_key, city_desc['id'])
        if len(locationTemp) == 0:
            print('Weather service is not available')
        print('Temperature of "%s" is %d* C' % locationTemp)
    return 0


if __name__ == "__main__":
    exit(main(cmd_args))
