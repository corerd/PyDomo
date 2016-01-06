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

'''Web server skeleton using SimpleHTTPServer and Bootstrap
with Basic Authentication and SSL support.

This web server skeleton is built on the Bootstrap Starter Template:
http://getbootstrap.com/examples/starter-template/

The above Bootstrap template has been customized to comply with
the Jinja2 template engine:
http://jinja.pocoo.org/docs/dev/


To run the web server, enter the following line:
python bootstrap-starter.py
'''

from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from jinja2 import Environment, PackageLoader, TemplateNotFound
from os import curdir, sep
import ssl
import base64

PORT_NUMBER = 4443
STATIC_FILE_DIR = 'static'

'''GLOBALS'''
auth_key = ""
static_endpoint = curdir + sep + STATIC_FILE_DIR

'''Create an instance of the JINJA Environment class:
http://jinja.pocoo.org/docs/dev/api/#basics

The loader looks up the templates in the templates folder
inside the application’s python package.

See also http://stackoverflow.com/a/6196098
and http://stackoverflow.com/a/9763688

If you are using a single module (as in this example),
__name__ is always the correct value.
If you however are using a package, it’s usually recommended
to hardcode the name of your package there.

The assignment below is module / package independent:
'''
app_package = __name__.split('.')[0]
jinja_env = Environment(
    loader=PackageLoader(app_package, 'templates'),
    trim_blocks=True,
    lstrip_blocks=True,
    extensions=['jinja2.ext.autoescape'])


class AuthHandler(SimpleHTTPRequestHandler):
    '''Main class to present webpages and basic authentication.

    https://gist.github.com/fxsjy/5465353
    '''
    def do_HEAD(self):
        '''send header'''
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_AUTHHEAD(self):
        '''send header'''
        self.send_response(401)
        self.send_header('WWW-Authenticate',
                         'Basic realm=\"Bootstrap starter demo\"')
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        ''' Present frontpage with user authentication. '''
        global auth_key
        if self.headers.getheader('Authorization') is None:
            self.do_AUTHHEAD()
            self.wfile.write('no auth header received')
        elif self.headers.getheader('Authorization') == 'Basic ' + auth_key:
            self.webpage_handle()
        else:
            self.do_AUTHHEAD()
            self.wfile.write(self.headers.getheader('Authorization'))
            self.wfile.write('not authenticated')

    def do_mimetype_HEAD(self, mimetype):
        '''send header according to mimetype'''
        self.send_response(200)
        self.send_header('Content-type', mimetype)
        self.end_headers()

    def webpage_handle(self):
        '''Handler for any other incoming request after authentication.

        Derived from: http://www.acmesystems.it/python_httpd
        '''
        if self.path == "/":
            self.path = "/bootstrap-starter.htm"

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
                    template = jinja_env.get_template(self.path)
                    self.do_mimetype_HEAD(mimetype)
                    self.wfile.write(template.render(proj_name=app_package))
                except TemplateNotFound as e:
                    self.send_error(404, 'Template Not Found: %s' % e.name)
            else:
                #Open the static file requested and send it
                static_file_path = static_endpoint + self.path
                try:
                    static_file = open(static_file_path)
                    self.do_mimetype_HEAD(mimetype)
                    self.wfile.write(static_file.read())
                    static_file.close()
                except IOError:
                    self.send_error(404, 'File Not Found: %s' % self.path)


def start_server(user, password, ssl_certificate, server_key):
    '''Create an HTTPS server server and
    define the handler to manage the incoming request.

    https://www.piware.de/2011/01/creating-an-https-server-in-python/
    '''
    global auth_key
    auth_key = base64.b64encode('%s:%s' % (user, password))
    httpd = HTTPServer(('', PORT_NUMBER), AuthHandler)
    httpd.socket = ssl.wrap_socket(httpd.socket,
                                   certfile=ssl_certificate,
                                   keyfile=server_key,
                                   server_side=True)
    print 'Started HTTPS server on port ', PORT_NUMBER
    # Debug at https://localhost:PORT/
    try:
        '''Wait forever for incoming http requests till CTRL-C is pressed'''
        httpd.serve_forever()
    except KeyboardInterrupt:
        print
        print 'Keyboard Interrupt received, shutting down the web server...'
        httpd.socket.close()


def main():
    start_server('pippo', 'pluto', './CA/server.crt', './CA/server.key')


if __name__ == "__main__":
    exit(main())
