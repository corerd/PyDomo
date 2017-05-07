Create a self-signed SSL Certificate
====================================
These shell scripts perform the steps displayed
[here](http://www.akadia.com/services/ssh_test_certificate.html).


Step 1: Generate a Private Key
------------------------------
```
ssl_gen_private_key.sh server.key.enc
```

Step 2: Generate a CSR (Certificate Signing Request)
----------------------------------------------------
```
ssl_gen_csr.sh domain server.key.enc server.csr
```

Step 3: Remove Passphrase from Key
----------------------------------
```
ssl_remove_passphrase.sh server.key.enc server.key
```

Step 4: Generating a Self-Signed Certificate
--------------------------------------------
```
ssl_gen_crt.sh server.key server.csr server.crt
```

Step 5: Installing the Private Key and Certificate
--------------------------------------------------
