#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''Bootstrap Demo
http://getbootstrap.com/examples/starter-template/
'''

from os.path import basename, splitext
from flask import Flask, render_template

this_module_name = splitext(basename(__file__))[0]
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('bootstrap-starter.html', proj_name=this_module_name)


if __name__ == "__main__":
    # if debug support is enabled, the server will reload itself on code changes,
    # and it will also provide you with a helpful debugger if things go wrong.
    app.debug = True

    app.run()