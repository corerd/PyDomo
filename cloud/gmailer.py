#!/usr/bin/env python
"""Send email via Gmail authenticating with OAuth2

Google provides the `oauth2.py` script and library to implement and debug OAuth2.
The script can be used as a standalone utility for generating and authorizing
OAuth tokens, and for generating OAuth2 authentication strings from OAuth tokens.

`oauth2.py` can be downloaded from the Google source
[repository](https://raw.githubusercontent.com/google/gmail-oauth2-tools/master/python/oauth2.py).
At the time of writing, the script works on Python 2.4 or greater,
but is not Python 3 compatible.

[Here](https://raw.githubusercontent.com/corerd/PyDomo/master/cloud/oauth2.py)
you can find an updated version of `oauth2.py` supporting both Python 2 and 3.

Instructions for using `oauth2.py` is available on the Google
[wiki](https://github.com/google/gmail-oauth2-tools/wiki/OAuth2DotPyRunThrough).


Generate OAuth2 Credentials
---------------------------
There are 2 types of Credentials:

- The **Client ID** and **Client secret** obtained registering the application
  on [Google Developers Console](https://console.developers.google.com).

- An authorizing **OAuth tokens** generated from the above Client ID and secret.


### Registering An Application

1. Open the [Google Developers Console](https://console.developers.google.com).

2. From the project drop-down, choose **Create a new project**, enter
   a name for the project, and optionally, edit the provided project ID.
   Click **Create**.

3. On the Credentials page, select **Create credentials**,
   then select **OAuth client ID**.

4. You may be prompted to set a product name on the Consent screen;
   if so, click **Configure consent screen**, supply the requested information,
   and click **Save** to return to the Credentials screen.

5. Select **Other** for the **Application type**, and enter any additional
   information required.

6. Click **Create**.

7. Click **OK** to dismiss the resulting pop-up showing the **client ID**
   and **client secret**.

8. Click the **Download JSON** button to the right of the client ID.

9. Move this file to your working directory and rename it `client_secret.json`.
"""

from __future__ import print_function
from builtins import input

import sys
import json
import ntpath
from datetime import datetime
from datetime import timedelta

import base64
import smtplib
import oauth2

#needed for attachment
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders


CLIENT_SECRET_FILE = 'client_secret.json'
GMAIL_AUTH_DATA = 'gmail_auth_data.json'
GMAIL_AUTH_TMP = 'gmail_auth_tmp.json'

GMAIL_SCOPE = 'https://mail.google.com/'
GMAIL_SMTP_SERVER = 'smtp.gmail.com'
SMTP_MSA_PORT = 587


def get_parm_value(key, dictionary):
    """Takes a dict with nested dicts, and searches all dicts for the key.
    See: https://stackoverflow.com/a/14962509

    Args:
        key: search key.
        dictionary: search dictionary.

    Returns:
        If the key is found, returns the associated value,
        otherwise None.
    """
    if key in dictionary: return dictionary[key]
    for k, v in dictionary.items():
        if isinstance(v,dict):
            return get_parm_value(key, v)


def get_auth_parms(json_file, *kparms, **kwverbose):
    """Gets authorization parameters from the given json_file,
    expected fields listed in kparms.

    Args:
        json_file: JSON formatted parameters file.
        kparms: an arbitrary number of parameters keys.
        kwverbose: keyword argument 'verbose':
                        if True, print debug informations to stderr.

    Returns:
        A tuple (parms, invalid).

        'parms' is a dictionary of authorization parameters get from 'json_file'
        and indexed by 'kparms' keys.
        If the 'json_file' doesn't exist, 'parms' is set to None.

        'invalid' is set to True if some field is missing.

    Remark:
        For Python 2 & 3 compatibility, defining functions with a variable number
        of arguments, their default values must be specify as keyword arguments.
        See: https://stackoverflow.com/a/15302038
    """
    # Pop 'verbose' out of keyword arguments (set default value to False).
    verbose = kwverbose.pop('verbose', False)

    parms = None
    invalid = False
    parms_dataset = None
    try:
        with open(json_file, 'r') as parms_file:
            parms = {}
            parms_dataset = json.load(parms_file)
            for pkey in kparms:
                value = get_parm_value(pkey, parms_dataset)
                parms[pkey] = value
                if value is None:
                    invalid = True
    except IOError:
        # JSON file doesn't exist: 'parms' is set to None.
        pass
    except ValueError:
        # JSON file couldn't be decoded: 'invalid' is set to True.
        invalid = True

    if verbose is True:
        if parms is None:
            print("'%s' doesn't exist." % json_file, file=sys.stderr)
        else:
            if parms_dataset is None:
                print("'%s' couldn't be decoded as JSON file." % json_file,
                                                            file=sys.stderr)
            else:
                print("JSON file '%s' decoded as:" % json_file, file=sys.stderr)
                print( json.dumps( parms_dataset,
                            sort_keys=True, indent=4, separators=(',', ': ') ),
                        file=sys.stderr )
                print("Requested fields:", file=sys.stderr)
                print( json.dumps( parms,
                            sort_keys=True, indent=4, separators=(',', ': ') ),
                        file=sys.stderr )
                if invalid is True:
                    print('Some field is missing.', file=sys.stderr)
        print()

    return (parms, invalid)


class DataStoreError(Exception):
    """Base class for exceptions in DataStore class."""
    pass


class CredentialsError(DataStoreError):
    """Exception raised getting credentials from DataStore."""
    pass


class SMTPAuthError(DataStoreError):
    """Exception raised sending SMTP AUTH Command.

    Attributes:
        ecode -- error code
        emsg  -- explanation of the error
        imsg  -- explanation of the intermediate response error
    """
    def __init__(self, ecode, emsg, imsg):
        self.ecode = ecode
        self.emsg = emsg
        self.imsg = imsg

    def __str__(self):
        mesg = ''
        if len(self.imsg) > 0:
            mesg = 'SMTP AUTH retcode (334): {}\n'.format(self.imsg)
        mesg = mesg + 'SMTP AUTH retcode ({}): {}'.format(self.ecode, self.emsg)
        return mesg


class DataStore(object):
    DATE_TIME_FMT = '%Y-%m-%d %H:%M:%S.%f'

    def __init__(self, debug=False):
        self.debug = debug
        self.client_id = None
        self.client_secret = None
        self.user_email = None
        self.refresh_token = None
        self.access_token = None
        self.access_token_expire = None
        secrets, invalid = get_auth_parms( CLIENT_SECRET_FILE,
                                            'client_id',
                                            'client_secret',
                                            verbose=self.debug )
        if secrets is None or invalid is True:
            raise DataStoreError("File '%s' is missing or invalid!" %
                                    CLIENT_SECRET_FILE)
        self.client_id = secrets['client_id']
        self.client_secret = secrets['client_secret']

    def checkin(self):
        """Obtains user_email, access_token and refresh_token
        from authorization json data files.
        """
        auth_data, invalid = get_auth_parms( GMAIL_AUTH_DATA,
                                                'user_email',
                                                'refresh_token',
                                                verbose=self.debug )
        if auth_data is None or invalid is True:
            raise CredentialsError("File '%s' is missing or invalid!" %
                                        GMAIL_AUTH_DATA)
        self.user_email = auth_data['user_email']
        self.refresh_token = auth_data['refresh_token']
        try:
            self.load_access_token()
        except CredentialsError:
            # File containing access_token is missing or invalid.
            # Try to refresh access_token.
            self.refresh()

        # Check access_token expiration time
        expire_datetime = datetime.strptime(self.access_token_expire,
                                                self.DATE_TIME_FMT)
        if datetime.now() > expire_datetime:
            self.refresh()

    def setup(self):
        """Creates and Authorizes OAuth Tokens as credentials
        and stores them in json formatted data files.

        They are obtained:
            user_email
            refresh_token
            temporary access_token
            temporary access_token expiration time

        The refresh_token can be used over and over again until it is revoked.
        To view or revoke your OAuth tokens, visit this Google Accounts page:
        https://security.google.com/settings/security/permissions
        """
        print('Creating and Authorizing Tokens as Credentials.')
        print('To authorize token, visit this url and follow the directions:')
        print('  %s' % oauth2.GeneratePermissionUrl(self.client_id, GMAIL_SCOPE))
        authorization_code = input('Enter verification code: ')
        response = oauth2.AuthorizeTokens( self.client_id, self.client_secret,
                                            authorization_code )
        auth_data = {}
        auth_data['refresh_token'] = response['refresh_token']
        auth_data['user_email'] = input('Enter User e-mail: ')
        print()
        with open(GMAIL_AUTH_DATA, 'w') as auth_json_file:
            json.dump(auth_data, auth_json_file)
        self.store_access_token(response['access_token'], response['expires_in'])
        self.checkin()

    def refresh(self):
        """Obtains a new access_token given a refresh_token
        and stores with expiration time to a json formatted data file.
        """
        if self.debug is True:
            print('Refreshing the access token...')
        response = oauth2.RefreshToken( self.client_id, self.client_secret,
                                        self.refresh_token )
        if self.debug is True:
            print("Saving to '%s'\n" % GMAIL_AUTH_TMP)
        self.store_access_token(response['access_token'], response['expires_in'])
        self.load_access_token()

    def load_access_token(self):
        tmp_token, invalid = get_auth_parms( GMAIL_AUTH_TMP,
                                                'access_token',
                                                'access_token_expire',
                                                verbose=self.debug )
        if tmp_token is None or invalid is True:
            raise CredentialsError("File '%s' is missing or invalid!" %
                                        GMAIL_AUTH_TMP)
        self.access_token = tmp_token['access_token']
        self.access_token_expire = tmp_token['access_token_expire']

    def store_access_token(self, token, seconds):
        """Stores an access_token with expiration time
        to a json formatted data file.
        """
        expire_datetime = datetime.now() + timedelta(seconds=int(seconds))
        auth_data = {}
        auth_data['access_token'] = token
        auth_data['access_token_expire'] = \
                                expire_datetime.strftime(self.DATE_TIME_FMT)
        with open(GMAIL_AUTH_TMP, 'w') as auth_tmp_json_file:
            json.dump(auth_data, auth_tmp_json_file)

    def smtp_connect(self):
        """Connect to GMAIL_SMTP_SERVER.
        Requires Simple Authentication and Security Layer (SASL) XOAUTH2 Mechanism.

        Returns:
            The instance of the SMTP connection.

        SMTP Authentication Reply-Codes and their meaning according to
        [RFC 4954](https://tools.ietf.org/html/rfc4954):
            235	Authentication Succeeded
            334	Text part containing the [BASE64] encoded string
            432	A password transition is needed
            454	Temporary authentication failure
            500	Authentication Exchange line is too long
            501	Malformed auth input/Syntax error
            503	AUTH command is not permitted during a mail transaction
            504	Unrecognized authentication type
            530	Authentication required	Submission mode
            534	Authentication mechanism is to weak
            535	Authentication credentials invalid
            538	Encryption required for requested authentication mechanism

        References:
            https://developers.google.com/gmail/imap/xoauth2-protocol
            https://www.fehcom.de/qmail/smtpauth.html
            https://stackoverflow.com/a/15796888
        """
        smtp_conn = smtplib.SMTP(GMAIL_SMTP_SERVER, SMTP_MSA_PORT)
        if self.debug is True:
            print
            smtp_conn.set_debuglevel(True)
        smtp_conn.starttls()  # starts SSL encryption

        # Authenticates sending the SMTP AUTH Command:
        #       AUTH XOAUTH2 initial_response
        # XOAUTH2 is the SASL authentication mechanism.
        #
        # The SASL XOAUTH2 initial_response has the following format:
        # base64("user=" {User} "^Aauth=Bearer " {Access Token} "^A^A")
        # where ^A represents a Control+A (\001).
        auth_string = oauth2.GenerateOAuth2String( self.user_email,
                                                    self.access_token,
                                                    base64_encode=False )
        initial_response = base64.b64encode(auth_string.encode()).decode()
        retcode, retmsg = smtp_conn.docmd('AUTH', 'XOAUTH2 ' + initial_response)
        intermediate_response_msg = ''
        if retcode == 334:
            # Intermediate response to the AUTH command
            # containing an error message in the format: base64({JSON-Body}).
            # The JSON-Body contains three values: status, schemes and scope.
            intermediate_response_msg = base64.b64decode(retmsg).decode()
            if self.debug is True:
                print( 'reply: retcode (334); BASE64 decoded Msg',
                        intermediate_response_msg )
            # The SASL protocol requires clients to send an empty message
            # to an intermediate response.
            retcode, retmsg = smtp_conn.docmd('')

        if retcode is not 235:
            # Authentication didn't Succeed
            smtp_conn.quit()
            raise SMTPAuthError(retcode, retmsg, intermediate_response_msg)
        return smtp_conn


def send_mail(to_addr, subject, message_text_plain,
                    message_text_html='', attachment='', debug=False):
    """Send an email via Gmail OAuth.
    The sender's credentials are fetched up in DataStore.
    If this method doesn't raise an exception, the recipient should get the mail.

    Args:
        to_addr: the receiver's email address string.
                 If it is equal to 'me', it is replaced by the sender email.
        subject: the subject of the mail.
        message_text_plain: the message body as plain-text.
        message_text_html: the HTML version of the message body.
        attachment: the path to the file to be attached.
        debug: if True, print debug informations to stderr.

    Returns:
        A dictionary, with one entry for each recipient that was refused.
        Each entry contains a tuple of the SMTP error code
        and the accompanying error message sent by the server.

    References:
        https://stackoverflow.com/q/37201250
        http://naelshiab.com/tutorial-send-email-python/
        http://stackabuse.com/how-to-send-emails-with-gmail-using-python/

    See also Goole api: https://developers.google.com/gmail/api/guides/sending
    """
    ds = DataStore(debug)
    ds.checkin()
    if to_addr == 'me':
        to_addr = ds.user_email

    # Create message container
    msg = MIMEMultipart()
    msg['From'] = ds.user_email
    msg['To'] = to_addr
    msg['Subject'] = subject

    # Create the body of the message
    msg.attach(MIMEText(message_text_plain, 'plain'))

    # Creating the attachement
    if len(attachment) > 0:
        attachment_file_name = ntpath.basename(attachment)
        attachment_content = open(attachment, "rb")
        part = MIMEBase('application', 'octet-stream')
        part.set_payload((attachment_content).read())
        encoders.encode_base64(part)
        part.add_header( 'Content-Disposition', "attachment; filename= %s" %
                                                        attachment_file_name )
        msg.attach(part)

    # Encode the message (the message should be in bytes)
    raw_msg = msg.as_string()

    # Send the message
    smtp_server = ds.smtp_connect()
    refused = smtp_server.sendmail(ds.user_email, to_addr, raw_msg)
    try:
        smtp_server.quit()
    except Exception:
        # Error codes and messages already catch in refused dictionary
        pass
    return refused


def test_configuration():
    """Check OAuth2 credentials DataStore integrity and then
    try to connect the Gmail SMTP server.
    """
    print('>>>>>>>> Check DataStore integrity')
    try:
        ds = DataStore(debug=True)
    except DataStoreError as e:
        print('DataStore ERROR:', e)
        print("The file containing Clent Secrets is missing or invalid.")
        print("Register the application on Google Developers Console:")
        print("https://console.developers.google.com")
        print()
        print("Go to Credentials page, download the JSON file")
        print("and rename it as '%s'" % CLIENT_SECRET_FILE)
        print()
        return False

    try:
        ds.checkin()
    except CredentialsError as e:
        print('DataStore ERROR:', e)
        print('Files containing credentials are missing or invalid.')
        print()
        ds.setup()

    print('\n>>>>>>>> Testing SMTP authentication with OAuth2...')
    try:
        smtp_server = ds.smtp_connect()
    except SMTPAuthError as e:
        print('>>>>>>>> Denied!\n')
        print('\n{}'.format(e))
        return False
    print('>>>>>>>> Accepted!\n')
    smtp_server.quit()
    return True


def main():
    if test_configuration() is not True:
        return

    from random import randint
    print('\n>>>>>>>> Send a testing email with random content')
    subject = 'gmailer test {}'.format(randint(100, 999))
    msg = 'Hello Gmail at {}.'.format(datetime.now())
    refused = send_mail('me', subject, msg, debug=True)
    if len(refused) > 0:
        print('>>>>>>>> The recipient was refused')
        print(refused)
    else:
        print('>>>>>>>> Done!')


if __name__ == '__main__':
    main()
