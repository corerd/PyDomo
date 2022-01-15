"""Gmail API requests in Python

This script is both a client front-end library and a command-line application
to make requests to Gmail Google API.

Python 2,7 and 3.6 are fully supported and tested.
The script may work on other versions of Python 3 though not tested.

@TODO Get rid of pickled data format for token file
and use json instead, as in the new Gmail Python Quickstart tutorial
(https://developers.google.com/gmail/api/quickstart/python).


PREREQUISITES

Gmail API use the OAuth 2.0 protocol for authentication and authorization.

To enable Gmail API, follow the **Enable the Gmail API** wizard that you can
find in Gmail Python Quickstart tutorial
(https://developers.google.com/gmail/api/quickstart/python).

The wizard creates a new Cloud Platform project named **Quickstart**,
enables the Gmail API and returns the `credentials.json` file containing
the OAuth 2.0 credentials (that is **client ID** and **client secret**)
that are known to both Google and you.

Your client configuration can be later managed in
Google Cloud Console (https://console.cloud.google.com/iam-admin/iam)
and Google API Console (https://console.cloud.google.com/apis/dashboard).


OAUTH 2.0 AUTHORIZATION FLOW 

Before this script can access a Gmail API, it must obtain from the Google
Authorization Server an access_token that grants access to that API.

Such request requires an authentication step where the user logs in with his
Google account and submits his **client ID** and **client secret** credentials.
Then the user is asked whether he is willing to grant the permissions that
this script is requesting.

Since the access_token has limited lifetime, it always comes together
a refresh_token; they are stored in the `token.pickle` file for later use.

The access_token is sent to the Gmail API in an HTTP authorization header.

If this script needs access to a Gmail API beyond the lifetime of its access
token, it will proceed automatically requesting a new one from the Google
Authorization Server by means of the refresh_token without any further
user interaction.


EXPORTED FUNCTIONS

GetAuthTokens
    obtains OAuth 2.0 tokens from Google Authorization Server.

gmSend
    sends an unicode email message (more an optional attachment)
    from the user's account.

This script can also be run as a standalone command-line application to checkout
**OAuth 2.0 tokens** from Google Authorization Server.


CREDITS

How to send email with gmail API and python
https://stackoverflow.com/a/37267330


REFERENCES

Using OAuth 2.0 to Access Google APIs
https://developers.google.com/identity/protocols/OAuth2

Gmail Python API Quickstart to enable the Gmail API
https://developers.google.com/gmail/api/quickstart/python

Send an email message from the user's Gmail account
https://developers.google.com/gmail/api/v1/reference/users/messages/send


LICENSE

Copyright (c) 2019 Corrado Ubezio

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from __future__ import print_function

import os
import pickle
import base64
from sys import version_info
from os.path import dirname, exists, join, realpath, split

import mimetypes
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError


OAUTH_TOKEN_NAME = 'token.pickle'
OAUTH_CREDENTIAL_NAME = 'credentials.json'

CREDENTIAL_LOSS_MESSAGE = """
Your OAuth 2.0 credential file named {} is missing or invalid.
The first time, open the tutorial Gmail Python API Quickstart
    https://developers.google.com/gmail/api/quickstart/python
and go to the ENABLE THE GMAIL API wizard.

If the Gmail API has been already turned on, go to your Google API Console
    https://console.cloud.google.com/apis/dashboard
open Credentials tab and download OAuth client configuration.
"""

# Locate the client secret files in module directory
OAUTH_TOKEN_FILE = join(dirname(realpath(__file__)), OAUTH_TOKEN_NAME)
OAUTH_CREDENTIAL_FILE = join(dirname(realpath(__file__)), OAUTH_CREDENTIAL_NAME)

# The variable SCOPES controls the set of resources and operations
# that an access_token permits.
# If modifying these scopes, delete the OAUTH_TOKEN_FILE.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']


def GetAuthTokens(modeIsInteractive=False):
    """Obtain OAuth 2.0 tokens from the Google Authorization Server

    Args:
        modeIsInteractive: Enables the user consent process (must be attended).

    Returns:
        auth_tokens

    This function will search for the `token.pickle` file where are stored
    the OAuth 2.0 access and refresh tokens.

    If the access_token is expired, a new one will be requested by means of
    the refresh_token and saved together to the same file without any user
    interaction.

    If no valid **OAuth 2.0 tokens** are found (for instance the first run),
    this script searches for the credentials.json` file and, if found,
    will open your default browser submitting your OAuth 2.0 credentials
    to the Google Authorization Server and start the user consent process
    to obtain a new set of tokens that will be stored to a newly created
    `token.pickle` file.

    Consequent runs won't need the user interacting the browser and can
    return OAuth 2.0 tokens straight.

    The user consent process is enabled by the `modeIsInteractive` argument
    because it needs to be attended by the user who must log in with
    his Google account to allow the requested permissions.

    If this function executes unattended (for instance in a daemon), please
    set the `modeIsInteractive` argument to False; in this way, whenever the
    user consent process is required, this function won't hang waiting
    for user imputs returning None.

    This function returns None in all other cases where it fails to retrieve
    OAuth 2.0 tokens.


    TROUBLESHOOTING

    This app isn't verified

    At the beginning of the user consent process, the OAuth consent screen
    may show the warning **This app isn't verified** because it is requesting
    scopes that provide access to sensitive user data.
    Your application must eventually go through the **verification process**
    (https://support.google.com/cloud/answer/7454865)
    to remove that warning and other limitations.
    During the development phase you can continue past this warning by clicking
    **Advanced > Go to {Project Name} (unsafe)**.

    OAuth invalid_grant

    Sometimes the OAuth 2.0 Refresh Token request raises the invalid_grant
    exception.
    One possible solution is to delete the `token.pickle` file and obtain
    a new OAuth 2.0 tokens set from the Google Authorization Server.


    PYTHON 2 vs 3 COMPATIBILITY

    The `token.pickle` file is saved as pickled data.
    Pickle uses different protocols to convert your data to a binary stream.
    - In Python 2 there are 3 different protocols (0, 1, 2) and the
      default is 0.
    - In Python 3 there are 5 different protocols (0, 1, 2, 3, 4) and the
      default is 3.
    Therefore use protocol number 2 even in Python 3 to comply with Python 2.
    See: https://stackoverflow.com/a/25843743


    CREDITS
    This function derives from the tutorial:
    Gmail Python API Quickstart to enable the Gmail API
    https://developers.google.com/gmail/api/quickstart/python
    """
    auth_tokens = None
    if exists(OAUTH_TOKEN_FILE):
        with open(OAUTH_TOKEN_FILE, 'rb') as token_file:
            # OAUTH_TOKEN_FILE has been saved as pickled data
            # using protocol number 2 to comply with Python 2.x and 3.x
            # See: https://stackoverflow.com/a/25843743
            if version_info.major > 2:
                # Fix loading issue in Python 3.x
                # See: https://stackoverflow.com/a/41366785
                auth_tokens = pickle.load(token_file, encoding='iso-8859-1')
            else:
                auth_tokens = pickle.load(token_file)
    # Check the OAuth 2.0 tokens
    if not auth_tokens or not auth_tokens.valid:
        if auth_tokens and auth_tokens.expired and auth_tokens.refresh_token:
            # if tokens are available but access_token has expired
            # then obtain a new access_token by means of the refresh token
            try:
                # a granted refresh token might no longer work
                auth_tokens.refresh(Request())
            except RefreshError as e:
                if modeIsInteractive:
                    if 'invalid_grant' in e.args[0]:
                        print('invalid_grant:\n'
                        '\tRefresh token is invalid, expired or revoked!\n'
                        'Could be that the refresh token has not been used for 6 months'
                        'See: https://developers.google.com/identity/protocols/oauth2#expiration'
                        ''
                        'One possible solution is to delete the token file and'
                        're-launch this script to obtain a new OAuth 2.0 tokens set'
                        'from the Google Authorization Server.'
                        '')
                        return None
                raise
        else:
            # If there are no tokens available and the mode is interactive
            # then open the OAuth consent screen in default browser and
            # let the user log in (the `credentials.json` file is required)
            if exists(OAUTH_CREDENTIAL_FILE) and modeIsInteractive:
                flow = InstalledAppFlow.from_client_secrets_file(
                                            OAUTH_CREDENTIAL_FILE, SCOPES)
                auth_tokens = flow.run_local_server(port=0)
        # Save the tokens (if any) for the next run
        if auth_tokens:
            with open(OAUTH_TOKEN_FILE, 'wb') as token_file:
                # write OAUTH_TOKEN_FILE as pickled data
                # using protocol number 2 to comply with Python 2.
                # See: https://stackoverflow.com/a/25843743
                pickle.dump(auth_tokens, token_file, protocol=2)
    return auth_tokens


def SendMessage(service, user_id, message):
    """Send an email message by means of HTTP request

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        message: Message to be sent.

    Returns:
        Sent Message.

    Raise:
        errors.HttpError
    """
    message = (service.users().messages().send(userId=user_id, body=message)
            .execute())
    return message


def CreateMessage(sender, to, subject, message_text):
    """Create a unicode message for an email.

    Args:
        sender: Email address of the sender.
        to: Email address of the receiver.
        subject: The subject of the email message.
        message_text: The text of the email message.

    Returns:
        An object containing a base64url encoded email object.

    CREDITS
    This function derives from the Gmail API example:
    Send an email message from the user's Gmail account
    https://developers.google.com/gmail/api/v1/reference/users/messages/send
    """
    message = MIMEText(message_text, 'plain', _charset='utf-8')
    message['to'] = to
    message['from'] = sender
    message['subject'] = Header(subject, 'utf-8')

    # PYTHON 2 vs 3 COMPATIBILITY
    # In Python 3 b64encode accepts bytes and returns bytes.
    # Subsequent decode is required to merge with string (comply with Python 2).
    return {'raw': base64.urlsafe_b64encode(
                    message.as_string().encode('utf-8')).decode("utf-8")}


def CreateMessageWithAttachment(sender, to, subject, message_text, file_path):
    """Create a unicode message for an email with attachment.

    Args:
        sender: Email address of the sender.
        to: Email address of the receiver.
        subject: The subject of the email message.
        message_text: The text of the email message.
        file_path: The path to the file to be attached.

    Returns:
        An object containing a base64url encoded email object.

    CREDITS
    This function derives from the Gmail API example:
    Send an email message from the user's Gmail account
    https://developers.google.com/gmail/api/v1/reference/users/messages/send
    """
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = Header(subject, 'utf-8')

    msg = MIMEText(message_text, 'plain', _charset='utf-8')
    message.attach(msg)

    _, filename = split(file_path)
    content_type, encoding = mimetypes.guess_type(file_path)

    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'
    main_type, sub_type = content_type.split('/', 1)
    if main_type == 'text':
        fp = open(file_path, 'rb')
        msg = MIMEText(fp.read(), _subtype=sub_type)
        fp.close()
    elif main_type == 'image':
        fp = open(file_path, 'rb')
        msg = MIMEImage(fp.read(), _subtype=sub_type)
        fp.close()
    elif main_type == 'audio':
        fp = open(file_path, 'rb')
        msg = MIMEAudio(fp.read(), _subtype=sub_type)
        fp.close()
    else:
        fp = open(file_path, 'rb')
        msg = MIMEBase(main_type, sub_type)
        msg.set_payload(fp.read())
        fp.close()

    msg.add_header('Content-Disposition', 'attachment', filename=filename)
    message.attach(msg)

    # PYTHON 2 vs 3 COMPATIBILITY
    # In Python 3 b64encode accepts bytes and returns bytes.
    # Subsequent decode is required to merge with string (comply with Python 2).
    return {'raw': base64.urlsafe_b64encode(
                    message.as_string().encode('utf-8')).decode("utf-8")}


def gmSend(to, subject, message_text, attachedFilePath=None,
            modeIsInteractive=False):
    """Send a unicode email message from the user's account

    Args:
        to: Email address of the receiver.
        subject: The subject of the email message.
        message_text: The text of the email message.
        attachedFilePath: The path to the file to be attached.
        modeIsInteractive: Enables the user consent process (must be attended).

    Returns:
        Sent Message.
    
    This function creates a unicode email message with an optional attachment,
    obtains the OAuth 2.0 tokens and sends the message together with the
    access_token to the Gmail API.

    The first time, if modeIsInteractive is True, this function opens a browser
    to start the user consent process and then saves your OAuth 2.0 tokens.
    If no valid **OAuth 2.0 tokens** are found and / or the user does not grant
    the permission, the function rises exceptions.
    Consequent runs won't need the user interacting the browser and can send
    emails straight.
    """
    # Create a unicode email message with an optional attachment
    if attachedFilePath:
        mail_message = CreateMessageWithAttachment('me', to, subject,
                                            message_text, attachedFilePath)
    else:
        mail_message = CreateMessage('me', to, subject, message_text)

    # Obtain an authorized Gmail API service instance by means of OAuth tokens.
    #
    # To prevent to log many warning lines caused by:
    #   "file_cache is unavailable when using oauth2client >= 4.0.0 #299"
    # set cache_discovery to False as found here:
    # https://github.com/googleapis/google-api-python-client/issues/299#issuecomment-268915510
    #
    # An other way to silence the warning and keep enable the cache is here:
    # https://github.com/googleapis/google-api-python-client/issues/325#issuecomment-274349841
    service = build('gmail', 'v1', credentials=GetAuthTokens(modeIsInteractive),
                        cache_discovery=False)

    # Send the email
    return SendMessage(service, 'me', mail_message)


def main():
    print('Python {}.{}.{}'.format(version_info.major, version_info.minor,
                                    version_info.micro))
    print('Checkout Gmail API OAuth 2.0 tokens from Google Authorization Server')
    if not exists(OAUTH_CREDENTIAL_FILE):
        print(CREDENTIAL_LOSS_MESSAGE.format(OAUTH_CREDENTIAL_FILE))
        return
    # This is an attended command-line application, then set modeIsInteractive
    # to True allowing the GetAuthTokens() function, if required, to open
    # a browser to start the user consent process.
    auth_tokens = GetAuthTokens(modeIsInteractive=True)
    if auth_tokens:
        print('Done')
    else:
        print('OAuth 2.0 tokens check failure: some error occurred')


if __name__ == '__main__':
    main()
