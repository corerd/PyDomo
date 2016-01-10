PyDomo Web Server
=================

SSL certificate and private keys locations
------------------------------------------

### The certificate files are public
.crt file are sent to everything that connects.

1. Create `your_crt_files_dir` directory under `/etc/ssl/certs`
2. Set owner:group to `root:root` and `chmod 755`
3. Copy your .crt files in `/etc/ssl/certs/<your_crt_files_dir>`  
   and be sure their owner:group is set to `root:root` and `chmod 644`

### Private keys must have reading heavily restricted
First of all create a `ssl-cert` group and add your user to it.

1. Create `your_private_keys_dir` directory under `/etc/ssl/private/`
2. Set owner:group to `root:ssl-cert` and `chmod 710`
3. Copy your private keys files in `/etc/ssl/private/<your_private_keys_dir>`  
   and be sure their owner:group is set to `root:ssl-cert` and `chmod 640`

References
----------
[Permissions for SSL keys](http://superuser.com/a/556496 "Link to Super User")  
[Best location for SSL certificate and private keys](http://serverfault.com/a/259307 "Link to Server Fault")  
