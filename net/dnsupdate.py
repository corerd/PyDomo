#!/usr/bin/env python

# The MIT License (MIT)
#
# Copyright (c) 2015 Corrado Ubezio
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

'''IP update client for DNS services.
'''

from __future__ import print_function
import sys
import logging
from os import makedirs
from os.path import dirname, exists, join, realpath
from dtdns import DtDNS_server
from ipecho import get_my_public_ip

# Globals
VERSION = '1.0'
DEFAULT_CFG_FILE = 'dnsupdatecfg.json'
DEFAULT_CFG_FILE_PATH = join(dirname(realpath(__file__)), DEFAULT_CFG_FILE)

USAGE = """This is an automatic IP updater.
The DNS host details are listed in a configuration file in JSON format.
If none given, the configuration is read from the file:
    %s
""" % DEFAULT_CFG_FILE_PATH

LOG_FILE_NAME = 'dnsupdate.txt'


def dnsupdate(work_dir, certs_file, dns_service):
    if exists(work_dir) is not True:
        try:
            makedirs(work_dir)
        except OSError:
            print('Canoot create working directory: %s' % work_dir,
                file=sys.stderr)
            return 1

    logging.basicConfig(filename=work_dir + '/' + LOG_FILE_NAME,
                        format='%(asctime)s %(levelname)s %(message)s',
                        level=logging.DEBUG)

    server = DtDNS_server(certs_file, dns_service)
    dns_ip = server.get_dns_ip()
    if dns_ip is '':
        logging.error('Fail to get dns IP')
        return 1

    ext_ip = get_my_public_ip()
    if ext_ip is '':
        logging.error('Fail to get ext IP')
        return 1

    if dns_ip != ext_ip:
        server.set_dns_ip(ext_ip)
        logging.info('dns IP changes from %s to %s' % (dns_ip, ext_ip))

    print(ext_ip)
    return 0


def main():
    import json
    from utils.cli import cfg_file_arg

    options = cfg_file_arg(VERSION, USAGE, DEFAULT_CFG_FILE_PATH)
    try:
        json_data = open(options.cfg_file)
        cfg_data = json.load(json_data)
        json_data.close()
    except Exception as e:
        print('Unable to load configuration from file %s' % options.cfg_file,
            file=sys.stderr)
        print(e, file=sys.stderr)
        return 1

    return dnsupdate(cfg_data['working-dir'],
                        cfg_data['ssl-certs-file'],
                        cfg_data['dns-servers-list'][0])


if __name__ == '__main__':
    exit(main())