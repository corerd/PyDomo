#!/bin/bash

## Generate a CSR (Certificate Signing Request)
#
# http://www.akadia.com/services/ssh_test_certificate.html
# https://serversforhackers.com/self-signed-ssl-certificates
# https://www.sslshopper.com/article-most-common-openssl-commands.html


if [ "$#" -ne 3 ]
then
    echo "Syntax: $(basename "$0") DOMAIN IN_KEYFILE OUT_CSRFILE"
    echo "Illegal number of parameters"
    exit 1
fi

DOMAIN="$1"
IN_KEYFILE="$2"
OUT_CSRFILE="$3"

## Set CSR variables
# --- C = Country name (2 letter code)
# --- ST = State or Province Name (full name)
# --- O = Organization Name (eg, company)
SUBJ="
C=RP
ST=Neverland
O=corerd
localityName=Somewhere
commonName=$DOMAIN
organizationalUnitName=Forest Fruit
"
echo "Generate CSR file $OUT_CSRFILE"
openssl req -new -subj "$(echo -n "$SUBJ" | tr "\n" "/")" \
                    -key "$IN_KEYFILE" -out "$OUT_CSRFILE"
