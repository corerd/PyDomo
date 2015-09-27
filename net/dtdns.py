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

'''A simple dynamic dns client in Python for www.dtdns.com using SSL connection.

Derived from:
https://github.com/JeremR/dtdns-sync
'''

import socket
import ssl
import re


class DtDNS_server:
    def __init__(self, certs_file, server_cfg):
        self.certs_file = certs_file
        self.remote = server_cfg['server-url']
        self.port = int(server_cfg['server-port'])
        self.domain = server_cfg['domain']['host-url']
        self.passwd = server_cfg['domain']['password']

    def get_request_server(self, msg):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # require a certificate from the server
        ssl_sock = ssl.wrap_socket(s,
                                   ca_certs=self.certs_file,
                                   cert_reqs=ssl.CERT_REQUIRED)

        ssl_sock.connect((self.remote, self.port))

        cert = ssl_sock.getpeercert()
        if not cert or ('commonName', self.remote) not in cert['subject'][2]:
            raise Exception('InvaliCert')

        # Set a simple HTTP request -- use httplib in actual code.
        ssl_sock.write(msg)

        # read all the data returned by the server.
        next_sock_read = "1"
        data = []
        while next_sock_read:
            next_sock_read = ssl_sock.read()
            data.append(next_sock_read)

        # note that closing the SSLSocket will also close the underlying socket
        ssl_sock.close()

        return ''.join(data)

    def get_dns_ip(self):
        msg_get_ip = "GET /api/autodns.cfm?id=%s&pw=%s HTTP/1.1\nHost: www.dtdns.com\nUser-Agent: corerd-PyDomo\n\n" % (self.domain, self.passwd)
        data = self.get_request_server(msg_get_ip)

        reg = re.compile(".*Host (.*) now points to ([0-9\.]+[0-9]+).*", re.DOTALL)
        result = reg.match(data)
        ip = ''
        if result:
            #host = result.group(1)
            ip = result.group(2)
        return ip

    def set_dns_ip(self, ip):
        msg_set_ip="GET /api/autodns.cfm?id=%s&pw=%s&ip=%s HTTP/1.1\nHost: www.dtdns.com\nUser-Agent: corerd-PyDomo\n\n" % (self.domain, self.passwd, ip)
        self.get_request_server(msg_set_ip)


if __name__ == '__main__':
    pass
