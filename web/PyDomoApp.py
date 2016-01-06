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

'''PyDomo Web App server using SimpleHTTPServer and Bootstrap
with optional Basic Authentication support.
If authentication is requested, the sensitive data (user name and password)
are securely sent over the web using SSL certificates to encrypt net traffic.

This PyDomo Web App server is built on the Bootstrap Starter Template:
http://getbootstrap.com/examples/starter-template/

Such Bootstrap template is customized to comply with Jinja2 template engine:
http://jinja.pocoo.org/docs/dev/
'''

from __future__ import print_function

from os import curdir, sep, path
from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from jinja2 import Environment, PackageLoader, TemplateNotFound
from cameraman.camgrab import grabImage
import ssl
import urllib
import base64


'''Define the name of the directory for static files,
that is CSS, JavaScript files and so on.
'''
STATIC_FILES_DIR = 'static'


'''Define the name of the directory for template files.'''
TEMPLATE_FILES_DIR = 'templates'


'''Define the name of the application’s package or module.

STATIC_FILES_DIR and TEMPLATE_FILES_DIR must be created in your package
or next to your module.

If you are using a single module, __name__ is the correct value.
If you instead are using a package, it’s usually recommended
to hardcode the name of your package here.
The assignment below is module / package agnostic:
'''
APP_PACKAGE = __name__.split('.')[0]


'''Create an instance of the JINJA Environment class:
http://jinja.pocoo.org/docs/dev/api/#basics

See also http://stackoverflow.com/a/6196098
and http://stackoverflow.com/a/9763688
'''
JINJA_ENV = Environment(
    # Look up the templates in the templates directory
    # inside the application’s python package.
    loader=PackageLoader(APP_PACKAGE, TEMPLATE_FILES_DIR),

    # Remove the first newline after a block.
    trim_blocks=True,

    # Strip leading spaces and tabs from the start of a line to a block.
    lstrip_blocks=True,

    # The autoescape extension allows toggling the autoescape feature
    # from within the template.
    extensions=['jinja2.ext.autoescape'])


'''Define endpoint where address static resources'''
THIS_MODULE_DIR = path.dirname(__file__)
if THIS_MODULE_DIR == '':
    '''If empty, it is called as a single module,
    then set the current directory'''
    THIS_MODULE_DIR = curdir
THIS_MODULE_DIR = THIS_MODULE_DIR + sep
STATIC_ENDPOINT = THIS_MODULE_DIR + STATIC_FILES_DIR


# Globals
'''Create an instance of camera_desc_list'''
camera_desc_list = {}


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


def get_snapshots_list(cameras_list):
    '''Grab snapshots from a list of web cameras.
    The list of web cameras is read from the configuration file.

    Returns an image list encoded to base64 and interpolated in data URIs.
    '''
    snapshots_list = []
    for camera_desc in cameras_list:
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


class WebPagesHandler(SimpleHTTPRequestHandler):
    '''Main class to present webpages.
    http://www.acmesystems.it/python_httpd
    '''
    site_title = ""

    @classmethod
    def set_site_title(cls, site_title):
        cls.site_title = site_title

    @classmethod
    def get_site_title(cls):
        return cls.site_title

    def do_mimetype_HEAD(self, mimetype):
        '''send header according to mimetype'''
        self.send_response(200)
        self.send_header('Content-type', mimetype)
        self.end_headers()

    def do_GET(self):
        '''Handler for the GET requests'''
        if self.path == "/":
            self.path = "/PyDomoSvr-main.htm"

        #Check the file extension required and
        #set the right mime type
        sendReply = False
        is_jinja_template = False
        if self.path.endswith(".htm"):
            mimetype = 'text/html'
            is_jinja_template = True
            sendReply = True
        if self.path.endswith(".html"):
            mimetype = 'text/html'
            sendReply = True
        if self.path.endswith(".jpg"):
            mimetype = 'image/jpg'
            sendReply = True
        if self.path.endswith(".gif"):
            mimetype = 'image/gif'
            sendReply = True
        if self.path.endswith(".ico"):
            mimetype = 'image/x-icon'
            sendReply = True
        if self.path.endswith(".js"):
            mimetype = 'application/javascript'
            sendReply = True
        if self.path.endswith(".css"):
            mimetype = 'text/css'
            sendReply = True

        if sendReply is True:
            if is_jinja_template is True:
                #Render the template file and send it
                try:
                    template = JINJA_ENV.get_template(self.path)
                    self.do_mimetype_HEAD(mimetype)
                    self.wfile.write(template.render(
                        jpeg_base64_list=get_snapshots_list(camera_desc_list),
                        proj_name=WebPagesHandler.get_site_title()))
                except TemplateNotFound as e:
                        self.send_error(404, 'Template Not Found: %s' % e.name)
            else:
                #Open the static file requested and send it
                static_file_path = STATIC_ENDPOINT + self.path
                try:
                    static_file = open(static_file_path)
                    self.do_mimetype_HEAD(mimetype)
                    self.wfile.write(static_file.read())
                    static_file.close()
                except IOError:
                    self.send_error(404, 'File Not Found: %s' % self.path)


class WebAuthPagesHandler(WebPagesHandler):
    '''Wrap WebPagesHandler class to provide basic authentication.
    https://gist.github.com/fxsjy/5465353

    Use class methods:
    https://julien.danjou.info/blog/2013/guide-python-static-class-abstract-methods
    '''
    auth_key = ""

    @classmethod
    def set_auth_key(cls, auth):
        '''Pass the authorization credentials
        as an auth dictionary {"user-name" : "<site_admin_username>",
                               "password" : "<site_admin__password>"}
        '''
        cls.auth_key = base64.b64encode('%s:%s' %
                                    (auth['user-name'], auth['password']))

    @classmethod
    def get_auth_key(cls):
        return cls.auth_key

    def do_HEAD(self):
        '''send header'''
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_AUTHHEAD(self):
        '''send WWW-Authenticate header'''
        self.send_response(401)
        self.send_header('WWW-Authenticate',
                         'Basic realm=\"PyDomo\"')
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        ''' Present frontpage with user authentication. '''
        if self.headers.getheader('Authorization') is None:
            self.do_AUTHHEAD()
            self.wfile.write('no auth header received')
        elif self.headers.getheader('Authorization') == \
                                'Basic ' + WebAuthPagesHandler.get_auth_key():
            WebPagesHandler.do_GET(self)
        else:
            self.do_AUTHHEAD()
            self.wfile.write(self.headers.getheader('Authorization'))
            self.wfile.write('not authenticated')


class PyDomoApp:
    '''Web server skeleton class with optional Basic Authentication support.
    '''
    #def __init__(self, host_data, auth_data=None):
    def __init__(self, app_cfg, debug=False):
        '''Define the handler of the incoming request.
        '''
        global camera_desc_list
        camera_desc_list = app_cfg['cameras-list']
        WebPagesHandler.set_site_title(app_cfg['site']['title'])
        self.host_name = app_cfg['site']['host']['name']
        self.host_port = int(app_cfg['site']['host']['port'])
        if debug is True:
            '''Create an HTTP server'''
            self.httpd = HTTPServer((self.host_name, self.host_port),
                                                            WebPagesHandler)
        else:
            '''Create an HTTPS server
            https://www.piware.de/2011/01/creating-an-https-server-in-python/
            '''
            if not path.exists(app_cfg['site']['ssl']['keyfile']):
                raise Exception('PyDomoApp',
                    'Missing key file %s' % app_cfg['site']['ssl']['keyfile'])
            if not path.exists(app_cfg['site']['ssl']['certfile']):
                raise Exception('PyDomoApp',
                    'Missing cert file %s' % app_cfg['site']['ssl']['certfile'])

            WebAuthPagesHandler.set_auth_key(app_cfg['site']['auth'])
            self.httpd = HTTPServer((self.host_name, self.host_port),
                                                        WebAuthPagesHandler)
            self.httpd.socket = ssl.wrap_socket(self.httpd.socket,
                                   certfile=app_cfg['site']['ssl']['certfile'],
                                   keyfile=app_cfg['site']['ssl']['keyfile'],
                                   server_side=True)

    def run(self):
        '''Wait forever for incoming http requests till CTRL-C is pressed'''
        print('PyDomo server %s running on port %d' %
                                            (self.host_name, self.host_port))
        try:
            self.httpd.serve_forever()
        except KeyboardInterrupt:
            print(' Keyboard Interrupt detected!')
        finally:
            print('Shutting down the server...')
            #self.httpd.socket.close()
            self.httpd.server_close()


if __name__ == "__main__":
    pass
