#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
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

'''PyDomo Web server using Flask and Bootstrap

Flask is a micro webdevelopment framework for Python:
http://flask.pocoo.org/docs/0.10/
http://flask.pocoo.org/docs/0.10/quickstart/#a-minimal-application

Flask system-wide installation:
sudo pip install Flask


Bootstrap is an HTML, CSS, and JS framework for developing responsive,
mobile first projects on the web:
http://getbootstrap.com/

This web server skeleton is built on the Bootstrap Starter Template:
http://getbootstrap.com/examples/starter-template/

The above Bootstrap template has been customized to comply with
the Jinja2 template engine used by Flask:
http://flask.pocoo.org/docs/0.10/templating/


To run the web server, enter the following line:
python PyDomoSvr.py
'''

import urllib
import base64
from os.path import dirname, join, realpath
from functools import wraps
from flask import Flask, render_template, request, Response
from utils.cli import cfg_file_arg
from utils.configdataload import ConfigData
from cameraman.camgrab import grabImage

# Globals
VERSION = '1.0'
DEFAULT_CFG_FILE = 'PyDomoSvr.json'

DEFAULT_CFG_FILE_PATH = join(dirname(realpath(__file__)), DEFAULT_CFG_FILE)

USAGE = '''PyDomo Web Server


If no configuration file path is given, it will read:
    %s
''' % DEFAULT_CFG_FILE_PATH


'''Create an instance of the Flask class:
http://flask.pocoo.org/docs/0.10/api/#application-object

The first argument is the name of the application’s module or package.
If you are using a single module (as in this example),
__name__ is always the correct value.
If you however are using a package, it’s usually recommended
to hardcode the name of your package there.

The assignment below is module / package independent:
'''
app = Flask(__name__.split('.')[0])


'''Create an instance of the ConfigData class'''
app_cfg = ConfigData()


'''------------------- HTTP Basic Auth Decorator Begin -------------------------
http://flask.pocoo.org/snippets/8/
'''
def check_auth(username, password):
    """Check a valid username / password combination.

    The username and password are read from the configuration file.
    """
    return username == app_cfg.data['site-auth']['user-name'] and \
           password == app_cfg.data['site-auth']['password']



def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated
'''-------------------- HTTP Basic Auth Decorator End -----------------------'''


def binary2uri(binary_data):
    '''Convert a raw binary bytearray into a data URI
    to be embedded in a jinja template.
    http://stackoverflow.com/a/25141121

    An other approach can be found here:
    http://stackoverflow.com/a/12035037

    Returns the base64 encoded and interpolated binary_data.
    '''
    base64_data = base64.b64encode(binary_data)
    return '{}'.format(urllib.quote(base64_data.rstrip('\n')))


def get_snapshots_list():
    '''Grab snapshots from a list of web cameras.
    The list of web cameras is read from the configuration file.

    Returns an image list encoded to base64 and interpolated in data URIs.
    '''
    snapshots_list = []
    for camera_desc in app_cfg.data['cameras-list']:
        '''The properties (ip address, optional credentials) of each web camera
        are read from the configuration file as descriptor.
        '''
        grab_ok, jpg_image = grabImage(camera_desc)
        if not grab_ok:
            # grabImage returns errors
            # TODO error handler
            continue
        '''
        Snapshots are returned as jpeg bytearrays,
        then they are encoded to base64 and interpolated
        and appended to the list.
        '''
        snapshots_list.append(binary2uri(jpg_image))
    return snapshots_list


@app.route('/')
@requires_auth
def index():
    '''Register a view function for a given URL.
    http://flask.pocoo.org/docs/0.10/api/#flask.Flask.route

    Use route() decorator to tell Flask what URL should trigger our function.
    The function is given a name which is also used to generate URLs
    for that particular function.

    Returns the HTML document we want to display in the user’s browser.
    '''
    return render_template('PyDomoSvr-main.html',
        jpeg_base64_list=get_snapshots_list(),
        proj_name=app_cfg.data['site-title'])


def main():
    options = cfg_file_arg(VERSION, USAGE, DEFAULT_CFG_FILE_PATH)
    try:
        app_cfg.load(options.cfg_file)
    except:
        print 'Unable to load configuration from %s' % options.cfg_file
        return 1

    # if debug support enabled, the server will reload itself on code changes,
    # and it will also provide you with a helpful debugger if things go wrong.
    if options.debug is True:
        print 'Debug support is enabled'
        app.debug = True
    else:
        app.debug = False
    app.run()


if __name__ == "__main__":
    exit(main())
