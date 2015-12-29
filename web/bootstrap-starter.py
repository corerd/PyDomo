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

'''Web server skeleton using Flask and Bootstrap

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
python bootstrap-starter.py
'''

from os.path import basename, splitext
from flask import Flask, render_template

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


'''Get the module file name.
It will define the <title> and <navbar-brand> in the Bootstrap Starter Template
HTML document rendered by Jinja2.
'''
this_module_name = splitext(basename(__file__))[0]


'''Register a view function for a given URL.
http://flask.pocoo.org/docs/0.10/api/#flask.Flask.route

Use the route() decorator to tell Flask what URL should trigger our function.
The function is given a name which is also used to generate URLs
for that particular function.
'''
@app.route('/')
def index():
    '''Returns the HTML document we want to display in the user’s browser.'''
    return render_template('bootstrap-starter.html', proj_name=this_module_name)


if __name__ == "__main__":
    # if debug support is enabled, the server will reload itself on code changes,
    # and it will also provide you with a helpful debugger if things go wrong.
    app.debug = True

    app.run()