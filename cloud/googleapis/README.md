# Gmail API requests in Python

Google provides the [Gmail Python Quickstart](
https://developers.google.com/gmail/api/quickstart/python) tutorial where
you can find the `quickstart.py` sample application.

The `gmailapi.py` script derives from `quickstart.py`.
It is both a client front-end library and a command-line application.

As a standalone command-line application, the `gmailapi.py` script is intended
to checkout **OAuth 2.0 tokens** from Google Authorization Server.

The `gmailapi.py` script also exports utility functions that can be called
by any client front-end to make requests to **Gmail API**.

**Gmail API** relies upon [OAuth 2.0 protocol](http://tools.ietf.org/html/rfc6749)
for authentication and authorization.

The description of the OAuth 2.0 authorization scenarios that Google supports
can be found in [Using OAuth 2.0 to Access Google APIs](
https://developers.google.com/identity/protocols/OAuth2).


## Making requests to the Gmail API

First, you'll need a Google account with Gmail enabled.

To enable Gmail API you have to create a new **Cloud Platform project** in
[Google Cloud Console](https://console.cloud.google.com/iam-admin/iam)
and enable the Gmail API in
[Google API Console](https://console.cloud.google.com/apis/dashboard).

Here are the steps required to allow the `gmailapi.py` script to send Gmail API
requests.


### 1. Obtain OAuth 2.0 credentials from the Google Cloud Console

This step is required only once to turn on the Gmail API obtaining
the OAuth 2.0 credentials (that is **client ID** and **client secret**)
that are known to both Google and you.

Google has speeded up this process providing the **Enable the Gmail API** wizard
that you can find in the [Gmail Python Quickstart](
https://developers.google.com/gmail/api/quickstart/python) tutorial.

The wizard creates a new Cloud Platform project named **Quickstart** with
**quickstart-random-number** as ID, and automatically enables the Gmail API.

The project can be later renamed in your
[Google Cloud Console](https://console.cloud.google.com/iam-admin/iam),
while the project ID can no more be changed.

After the wizard has finished, you'll find the `credentials.json` file
saving your client configuration including **client ID** and **client secret**.

The client configuration of your project can be also downloaded any time from
the [Google API Console](https://console.cloud.google.com/apis/dashboard).


### 2. Install the Google Client Library

Run the following command to install the library using pip:
```
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```


### 3. Obtain OAuth 2.0 tokens from the Google Authorization Server

Before the `gmailapi.py` script performs its first Gmail API request,
it must obtain a set of **OAuth 2.0 tokens**, that is:
- an **access token** that grants limited lifetime access to the API;
- a **refresh token** allowing the script to obtain new access tokens.

The script opens your default browser and submits to Google Authorization Server
your **OAuth 2.0 credentials** saved in the `credentials.json` file.

After logging in with your Google account, an OAuth consent screen is presented
to you asking to grant the requested permissions. If you'll accept, the script
will store the received **OAuth 2.0 tokens** (not username and password)
in the `token.pickle` file.

Subsequent runs of the `gmailapi.py` script won't need the browser and can send
API request straight by means the **access token** that has limited lifetime.
If the script needs access to a Gmail API beyond the lifetime of its access token,
it will proceed automatically requesting a new one from the Google Authorization
Server by means of the **refresh token**.

[Refresh token expiration](
https://developers.google.com/identity/protocols/oauth2#expiration) deals about
the possibility that a granted **refresh token** stop working, that is:

- The user has revoked your app's access.
- The refresh token has not been used for six months.
- The user changed passwords and the refresh token contains Gmail scopes.
- The user account has exceeded a maximum number of granted (live) refresh tokens.


## The gmailapi.py library script

It is required the `credentials.json` file with your **client ID** and
**client secret** from [Google Cloud Console](
https://console.cloud.google.com/iam-admin/iam).

The script exports the following functions:
- `GetAuthTokens` to obtain OAuth 2.0 tokens from Google Authorization Server;
- `gmSend` to send an unicode email message from the user's account
   with optional attachment.

Before any Gmail API request, the script checks out the **OAuth 2.0 tokens** and,
if necessary, automatically obtains or refreshes them from Google Authorization
Server.
Then the script extracts a token from the response, and sends this token
to the Gmail API that you want to access.


### The command-line application

Run the `gmailapi.py` script as a standalone application to checkout
**OAuth 2.0 tokens** from Google Authorization Server.

Open a command-line window and run:
```
python gmailapi.py
```
The script searches for the `token.pickle` file to read the **access token** and,
if it is expired, a new one will be requested and saved to the same file
without any further user interaction.

If no valid **OAuth 2.0 tokens** are found, the script searches for the
`credentials.json` file and, if found, will start the user consent process
to obtain a new set of tokens, storing them to the `token.pickle` file.


## Supported Python Versions

Python 2,7 and 3.6 are fully supported and tested.
The `gmailapi.py` script may work on other versions of 3 though not tested.


## Troubleshooting

This [section](
https://developers.google.com/gmail/api/quickstart/python#troubleshooting)
in Google's **Gmail Python Quickstart** tutorial describes some issues
that you may encounter while attempting to run `gmailapi.py`.

The most common are dealt in the following.


### This app isn't verified

The OAuth consent screen that is presented to the you may show the warning
**This app isn't verified** if it is requesting scopes that provide access to
sensitive user data. These applications must eventually go through the
[verification process](https://support.google.com/cloud/answer/7454865)
to remove that warning and other limitations.
During the development phase you can continue past this warning by clicking
**Advanced > Go to {Project Name} (unsafe)**.


### OAuth invalid_grant

The [RFC 6749 OAuth 2.0](https://tools.ietf.org/html/rfc6749#section-5.2) spec
says about it:
```
invalid_grant
      The provided authorization grant (e.g., authorization
      code, resource owner credentials) or refresh token is
      invalid, expired, revoked, does not match the redirection
      URI used in the authorization request, or was issued to
      another client.
```
In [this](
https://blog.timekit.io/google-oauth-invalid-grant-nightmare-and-how-to-fix-it-9f4efaf1da35)
Timekit Blog post you can find a list of what might be wrong.

One possible solution is to delete the `token.pickle` file and obtain a new
**OAuth 2.0 tokens** set from the Google Authorization Server.


# Demo

You can find the `gmsend_test.py` command-line script that demonstrates how
to use the `gmailapi.py` library to send a test message to someone with
an optional attachment.

Usage:
```
gmsend_test.py <email-address-of-the-receiver> [attached-file-path]
```

Example: to send a test message to someone attaching the gmail-logo.png file,
open a command-line window and run:
```
python gmsend_test.py <email-address-of-the-receiver> gmail-logo.png
```


# Security advice

The `gmailapi.py` script doesn't save any username and password,
but it reads and writes the `credentials.json` and `token.pickle`files
that contain your personal Google account data.

Please, keep these files in a secure private location and
don't put their content in any public sharing service such as GitHub.


# Credits

[How to send email with gmail API and python](
https://stackoverflow.com/a/37267330) at Stack Overflow


# References

[Using OAuth 2.0 to Access Google APIs](
https://developers.google.com/identity/protocols/OAuth2)

[Gmail Python API Quickstart to enable the Gmail API](
https://developers.google.com/gmail/api/quickstart/python)

[Send an email message from the user's Gmail account](
https://developers.google.com/gmail/api/v1/reference/users/messages/send)


# License

Copyright (c) 2019 Corrado Ubezio

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at [Apache Software Foundation](
http://www.apache.org/licenses/LICENSE-2.0).

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
