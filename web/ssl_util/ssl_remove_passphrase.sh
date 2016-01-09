#!/bin/bash

## Remove a pass phrase from a key
## Optionally create a copy of the same removing the pass phrase.
#
# http://www.akadia.com/services/ssh_test_certificate.html
# https://serversforhackers.com/self-signed-ssl-certificates
# https://www.sslshopper.com/article-most-common-openssl-commands.html

# A blank passphrase: change with your own
PASSPHRASE=''

if [[ "$#" -ne 2 ]]
then
    echo "Syntax: $(basename "$0") KEYFILE_PASSPHRASE_PROTECTED KEYFILE_PASSPHRASE_FREE"
    echo "Iillegal number of arguments!"
    exit 1
fi

KEYFILE_PASSPHRASE_PROTECTED="$1"
KEYFILE_PASSPHRASE_FREE="$2"
if [ "$KEYFILE_PASSPHRASE_FREE" == "$KEYFILE_PASSPHRASE_PROTECTED" ]
then
    echo "Syntax: $(basename "$0") KEYFILE_PASSPHRASE_PROTECTED KEYFILE_PASSPHRASE_FREE"
    echo "Protected and free key files must be different!"
    exit 1
fi

echo "#### PEM pass phrase free Private Key file in $KEYFILE_PASSPHRASE_FREE"
openssl rsa -in "$KEYFILE_PASSPHRASE_PROTECTED" -out "$KEYFILE_PASSPHRASE_FREE" -passin pass:$PASSPHRASE
