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
Login as root and create `ssl` directory under `/srv/<your_web_conf>/`
if it doesn't already exist.

Set `/srv/<your_web_conf>/ssl` owner:group to `root:root` and `chmod 755`.

### The certificate files are public
.crt file are sent to everything that connects.

1. Create `certs` directory under `/srv/<your_web_conf>/ssl/`
2. Set owner:group to `root:root` and `chmod 755`
3. Copy your .crt files in`/srv/<your_web_conf>/ssl/certs/`  
   and be sure their owner:group is set to `root:root` and `chmod 644`

### Private keys must have reading heavily restricted
First of all create a `ssl-cert` group and add your user to it.

1. Create `private` directory under `/srv/<your_web_conf>/ssl/`
2. Set owner:group to `root:ssl-cert` and `chmod 710`
3. Copy your private keys files in `/srv/<your_web_conf>/ssl/private/`  
   and be sure their owner:group is set to `root:ssl-cert` and `chmod 640`

References
----------
[How to create a self-signed SSL Certificate](http://www.akadia.com/services/ssh_test_certificate.html)

[Permissions for SSL keys](http://superuser.com/a/556496 "Link to Super User")  

[Best location for SSL certificate and private keys](http://serverfault.com/a/259307 "Link to Server Fault")  
