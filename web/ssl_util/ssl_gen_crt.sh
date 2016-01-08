#!/bin/bash

## Generate a Self-Signed SSL Certificate
#
# http://www.akadia.com/services/ssh_test_certificate.html
# https://serversforhackers.com/self-signed-ssl-certificates
# https://www.sslshopper.com/article-most-common-openssl-commands.html

if [ "$#" -ne 3 ]
then
    echo "Syntax: $(basename "$0") IN_KEYFILE IN_CSRFILE OUT_CRTFILE"
    echo "Illegal number of parameters"
    exit 1
fi

IN_KEYFILE="$1"
IN_CSRFILE="$2"
OUT_CRTFILE="$3"

echo "Generate a Self-Signed CRT file $OUT_CRTFILE"
openssl x509 -req -days 365 -signkey "$IN_KEYFILE" \
                    -in "$IN_CSRFILE" -out "$OUT_CRTFILE"
