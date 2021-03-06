PyDomo Web Server
=================

Setup
-----
The server configuration data is stored in the `PyDomoSvr.json` file
whose template is provided as `PyDomoSvr.json.template`.

Since the `PyDomoSvr.json` file contains sensitive data such as user passwords,
it must have reading **heavily restricted**.

1. Login as root and create `<your_web_conf>` directory as `PyDomoSvr` under `/srv/`
2. Set owner:group to `root:root` and `chmod 755`
3. Copy `PyDomoSvr.json.template` in  `/srv/PyDomoSvr/PyDomoSvr.json`
4. Set owner:group `root:root` and `chmod 600`
5. Customize the fields inside of `PyDomoSvr.json` according your needs.

Launch
------
`PyDomoSvrLaunch.py -c /srv/PyDomoSvr/PyDomoSvr.json`


SSL certificate
===============
To enable HTTPS on website, an SSL certificate is required.

This certificate may be self created and signed, but in this way all the browsers
will show *“This Connection is Untrusted”* errors for the website.
About this matter, you can find a bunch of utilities in the `ssl_util` directory.

To hush the browsers, the certificate must be provided by a Certificate Authority (CA).
[Let’s Encrypt](https://letsencrypt.org) is a free, automated, and open CA.

The [Certbot](https://certbot.eff.org/#arch-other) ACME client automates
*Let's Encrypt* certificates issuance and installation.

To obtain a cert using a built-in `standalone` webserver
(you may need to temporarily stop your existing webserver, if any):
```
$ sudo certbot certonly --standalone -d <your-domain>
```
All generated keys and issued certificates can be found
in `/etc/letsencrypt/live/<your-domain>`.

After a renewal, the latest necessary files are saved in
`/etc/letsencrypt/live/<your-domain>-<XYWZ>`
where `<XYWZ>` is a renewal counter.


PyDomo SSL configuration
------------------------
Open `/srv/PyDomoSvr/PyDomoSvr.json` and set the following fields:
```
"ssl": {
    "certfile" : "/etc/letsencrypt/live/<your-domain>-<XYWZ>/cert.pem",
    "keyfile" : "/etc/letsencrypt/live/<your-domain>-<XYWZ>/privkey.pem"
},
```


References
----------
[Let’s Encrypt](https://letsencrypt.org)

[Automatically enable HTTPS on your website with EFF's Certbot, deploying Let's Encrypt certificates.](https://certbot.eff.org)

[Location of the certificates generated by Cerbot](https://certbot.eff.org/docs/using.html#where-are-my-certificates)
