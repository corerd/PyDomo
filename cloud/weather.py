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

import logging
import urllib2
import json
import sys
from os.path import join

from cloudcfg import ConfigDataLoad


def wu_getConditions(log_file, user_api_key, country, city):
    """Get the current temperature in Celsius degrees using Weather Underground API.
    Weather Underground home: "https://www.wunderground.com/weather/api

    Data are logged in CSV format: datetime;city;temperature
    Return value is 0 for SUCCESS, -1 otherwise
    """
    wu_request_url = 'http://api.wunderground.com/api/%s/geolookup/conditions/q/%s/%s.json' % \
                                                ( user_api_key, country, city )
    logging.basicConfig(filename=log_file,
                        format='%(asctime)s %(levelname)s;%(message)s',
                        level=logging.DEBUG)
    try:
        f = urllib2.urlopen(wu_request_url)
        json_string = f.read()
        f.close()
    except:
        # See: http://stackoverflow.com/a/4990739
        logging.error("urllib2 error;%s" % sys.exc_info()[0])
        return -1
    try:
        parsed_json = json.loads(json_string)
        location = parsed_json['location']['city']
        temp_c = parsed_json['current_observation']['temp_c']
    except:
        # See: http://stackoverflow.com/a/4990739
        logging.error("parse json error;%s" % sys.exc_info()[0])
        return -1
    logging.info("%s;%s" % (location, temp_c))
    return 0

def main():
    cfg = ConfigDataLoad("cloudcfg.json")
    log_file = join(cfg.data['datastore'], "temperature.txt")
    return wu_getConditions(log_file,
                            cfg.data['wu-api-key'],
                            cfg.data['wu-search-country'],
                            cfg.data['wu-search-city'])

if __name__ == "__main__":
    status = main()
    if status == 0:
        print 'Done!'
    else:
        print 'FAIL!'
    exit(status)
