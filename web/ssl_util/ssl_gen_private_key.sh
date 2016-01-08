#!/bin/bash

## Generate a Private Key protected by PEM pass phrase.
## Optionally create a copy of the same removing the pass phrase.
#
# http://www.akadia.com/services/ssh_test_certificate.html
# https://serversforhackers.com/self-signed-ssl-certificates
# https://www.sslshopper.com/article-most-common-openssl-commands.html


if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]
then
    echo "Syntax: $(basename "$0") KEYFILE_PASSPHRASE_PROTECTED [KEYFILE_PASSPHRASE_FREE]"
    echo "illegal number of arguments!"
    exit 1
fi

KEYFILE_PASSPHRASE_PROTECTED="$1"
if [ -z "$2" ]
then
    KEYFILE_PASSPHRASE_FREE=""
else
    if [ "$2" == "$KEYFILE_PASSPHRASE_PROTECTED" ]
    then
        echo "Syntax: $(basename "$0") KEYFILE_PASSPHRASE_PROTECTED [KEYFILE_PASSPHRASE_FREE]"
        echo "Protected and free key files must be different!"
        exit 1
    fi
    KEYFILE_PASSPHRASE_FREE="$2"
fi

echo "#### Generate the Private Key file $KEYFILE_PASSPHRASE_PROTECTED (PEM pass phrase protected)"
openssl genrsa -aes256 -out "$KEYFILE_PASSPHRASE_PROTECTED" 2048

if [ ! $? -eq 0 ]
then
    exit 1
fi

if [ ! -z "$KEYFILE_PASSPHRASE_FREE" ]
then
    echo "#### PEM pass phrase free Private Key file in $KEYFILE_PASSPHRASE_FREE"
    openssl rsa -in "$KEYFILE_PASSPHRASE_PROTECTED" -out "$KEYFILE_PASSPHRASE_FREE"
fi
