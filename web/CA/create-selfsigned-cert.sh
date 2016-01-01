#!/bin/sh

# How to create a self-signed SSL Certificate
# http://www.akadia.com/services/ssh_test_certificate.html

echo "#### Step 1: Generate a Private Key"
openssl genrsa -des3 -out server.key 1024
echo "#### Done!"

echo "#### Step 2: Generate a CSR (Certificate Signing Request)"
echo "#### IT IS IMPORTANT THAT THE common name FIELD BE FILLED IN"
echo "#### WITH THE FULLY QUALIFIED DOMAIN NAME OF THE SERVER."
echo "#### IF THE WEBSITE TO BE PROTECTED WILL BE https://my.server.com,"
echo "#### THEN ENTER my.server.com AT THIS PROMPT."
openssl req -new -key server.key -out server.csr
echo "#### Done!"

echo "#### Step 3: Remove Passphrase from Key"
cp server.key server.key.org
openssl rsa -in server.key.org -out server.key
echo "#### Done!"

echo "#### Step 4: Generating a Self-Signed Certificate"
openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt
echo "#### Done!"

echo "#### Step 5: Installing the Private Key and Certificate"
echo "#### See: http://gagravarr.org/writing/openssl-certs/others.shtml#ca-openssl"
echo "#### See: https://www.debian-administration.org/article/284/Creating_and_Using_a_self_signed__SSL_Certificates_in_debian"
echo "#### TODO"
