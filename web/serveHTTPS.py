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

'''Serve HTTPS *directly* from Flask (no nginx, no apache, no gunicorn)
http://flask.pocoo.org/snippets/111/
'''

from os import path
import sys
import traceback

import ssl
#from OpenSSL import SSL
'''Require:
    libffi-dev
    libssl-dev

    install cryptography:
        pip install cryptography
'''


def load_certificate():
    '''Load SSL private key and certificate.
    They must be stored in the Certificate Authority (CA) directory:
        <module_dirname>/CA

    Return SSL context, None if fail creating
    '''
    ca_dir = path.join(path.dirname(__file__), 'CA')
    try:
        # using OpenSSL
        # context = SSL.Context(SSL.TLSv1_METHOD)
        # context.use_privatekey_file(path.join(ca_dir, 'server.key'))
        # context.use_certificate_file(path.join(ca_dir, 'server.crt'))

        # using ssl
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.load_cert_chain(path.join(ca_dir, 'server.crt'),
                                       path.join(ca_dir, 'server.key'))
    except:
        context = None
        print "Exception in certificate loading:"
        print '-'*60
        traceback.print_exc(file=sys.stdout)
        print '-'*60
    return context
