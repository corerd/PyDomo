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
import datetime

import base64
import smtplib
import oauth2


SCOPE = 'https://mail.google.com/'
CLIENT_SECRET_FILE = 'client_secret.json'
GMAIL_AUTH_DATA = 'gmail_auth_data.json'
GMAIL_AUTH_TMP = 'gmail_auth_tmp.json'


def get_secrets():
    """Gets client secrets from CLIENT_SECRET_FILE.

    Returns:
        A tuple (client, invalid).

        'client' is a dictionary with the fields 'id' and 'secret' get
        from the json client secret file.
        If the file doesn't exist, 'client' is set to None.

        'invalid' is set to True if some field is missing.

    # WARNING: Python methods will return NoneType expecting a tuple from them
    and fail to return anything to fill them up, that is 'client' set to None.
    Call this method using the [trick](https://stackoverflow.com/a/1274887).
    """
    client = None
    invalid = True
    try:
        with open(CLIENT_SECRET_FILE, 'rt') as secret_file:
            client_secret = json.load(secret_file)
            client = {}
            client['id'] = client_secret['installed']['client_id']
            client['secret'] = client_secret['installed']['client_secret']
            invalid = False
    except IOError:
        # JSON file doesn't exist: 'client' is set to None.
        pass
    except KeyError:
        # Some dictionary field is missing: 'invalid' is set to True.
        pass
    return (client, invalid)


def get_credentials():
    """Gets authorization data from GMAIL_AUTH_FILE

    Returns:
        A tuple (auth, invalid).

        'auth' is a dictionary with the fields 'user', 'access_token'
        and 'refresh_token' get from the json Gmail authorization file.
        If the file doesn't exist, 'auth' is set to None.

        'invalid' is set to True if some field is missing.

    # WARNING: Python methods will return NoneType expecting a tuple from them
    and fail to return anything to fill them up, that is 'auth' set to None.
    Call this method using the [trick](https://stackoverflow.com/a/1274887).
    """
    auth = None
    invalid = False
    try:
        with open(GMAIL_AUTH_FILE, 'rt') as auth_file:
            auth = {}
            auth_dataset = json.load(auth_file)
            try:
                auth['user'] = auth_dataset['user_email']
            except KeyError:
                auth['user'] = None
                invalid = True
            try:
                auth['access_token'] = auth_dataset['oauth']['access_token']
            except KeyError:
                auth['access_token'] = None
                invalid = True
            try:
                auth['refresh_token'] = auth_dataset['oauth']['refresh_token']
            except KeyError:
                auth['refresh_token'] = None
                invalid = True
    except IOError:
        # JSON file doesn't exist: 'auth' is set to None.
        pass
    except ValueError:
        # JSON file could be decoded: 'invalid' is set to True.
        invalid = True
    return (auth, invalid)


def smtp_open(user, auth_string):
  """Opens a SMTP connection authenticating with the given auth_string.

  Args:
    user: The Gmail username (full email address)
    auth_string: A valid OAuth2 string, not base64-encoded, as returned by
        GenerateOAuth2String.

  Returns:
    An SMTP instance.
  """
  print
  smtp_conn = smtplib.SMTP('smtp.gmail.com', 587)
  smtp_conn.set_debuglevel(True)
  smtp_conn.ehlo('')
  smtp_conn.starttls()
  smtp_conn.docmd('AUTH', 'XOAUTH2 ' + base64.b64encode(auth_string))
  return smtp_conn


def send_mail(sender, to, subject, message_text_plain,
                                        message_text_html='', attached_file=''):
    """
    See: http://naelshiab.com/tutorial-send-email-python/
         http://stackabuse.com/how-to-send-emails-with-gmail-using-python/
         https://stackoverflow.com/q/12827548

    Goole api: https://developers.google.com/gmail/api/guides/sending
    """
    #TestSmtpAuthentication(options.user,
    #    GenerateOAuth2String(options.user, options.access_token,
    #                         base64_encode=False))
    #smtp_conn.sendmail('from@test.com', 'to@test.com', 'cool')
    pass


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


def test_smtp_authentication(user, auth_string, verbose=False):
    """Authenticates to SMTP with the given auth_string by means of
    Simple Authentication and Security Layer (SASL) XOAUTH2 Mechanism.
    See: https://developers.google.com/gmail/imap/xoauth2-protocol
         https://www.fehcom.de/qmail/smtpauth.html

    Args:
        auth_string: a valid OAuth2 string, not base64-encoded, as returned by
                     GenerateOAuth2String.
        verbose: if True, print debug informations

    Returns:
        2-tuple composed of a numeric reply code and the actual reply line
        (multiline responses are joined into one long line).

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
    """
    smtp_conn = smtplib.SMTP('smtp.gmail.com', 587)
    if verbose is True:
        print
        smtp_conn.set_debuglevel(True)
    smtp_conn.ehlo('test')
    smtp_conn.starttls()

    # The SMTP AUTH Command:
    # AUTH XOAUTH2 initial_response
    #
    # XOAUTH2 is the SASL authentication mechanism.
    #
    # The SASL XOAUTH2 initial_response has the following format:
    # base64("user=" {User} "^Aauth=Bearer " {Access Token} "^A^A")
    # where ^A represents a Control+A (\001).
    initial_response = base64.b64encode(auth_string.encode()).decode()
    retcode, retmsg = smtp_conn.docmd('AUTH', 'XOAUTH2 ' + initial_response)
    if retcode == 334:
        # Intermediate response to the AUTH command
        # containing an error message in the format: base64({JSON-Body}).
        # The JSON-Body contains three values: status, schemes and scope.
        if verbose is True:
            print( 'reply: retcode (334); BASE64 decoded Msg',
                                base64.b64decode(retmsg).decode() )
        # The SASL protocol requires clients to send an empty message
        # to an intermediate response.
        retcode, retmsg = smtp_conn.docmd('')

    if retcode == 235:
        # Authentication Succeeded
        print()
        print('Send email')
        recipient_reply = smtp_conn.sendmail(user, user, 'Hello Gmail')
        if len(recipient_reply) > 0:
            print('Some recipient was refused:')
            print(recipient_reply)

    return retcode, retmsg


def set_oauth_configuration(config_file, secrets):
    scope = 'https://mail.google.com/'
    print('To authorize token, visit this url and follow the directions:')
    print('  %s' % oauth2.GeneratePermissionUrl(secrets['client_id'], scope))
    authorization_code = input('Enter verification code: ')
    response = oauth2.AuthorizeTokens( secrets['client_id'], secrets['client_secret'],
                                        authorization_code )
    expire_seconds = int(response['expires_in'])
    auth_data = {}
    auth_data['refresh_token'] = response['refresh_token']
    auth_data['access_token'] = response['access_token']
    auth_data['access_token_expire'] = \
            str(datetime.datetime.now() + datetime.timedelta(seconds=expire_seconds))
    auth_data['user_email'] = input('Enter User e-mail: ')
    with open(config_file, 'w') as outfile:
        json.dump(auth_data, outfile)
    print
    return get_auth_parms( config_file,
                            'user_email',
                            'access_token',
                            'refresh_token',
                            verbose=True )


def refresh_configuration(config_file, secrets):
    """Obtains a new token given a refresh token.
    Expected fields in config_file include 'access_token', 'expires_in', and 'refresh_token'.
    """
    auth_data = {}
    with open(config_file, 'r') as auth_json_file:
        auth_data = json.load(auth_json_file)
    response = oauth2.RefreshToken( secrets['client_id'], secrets['client_secret'],
                                    auth_data['refresh_token'] )
    expire_seconds = int(response['expires_in'])
    auth_data['access_token'] = response['access_token']
    auth_data['access_token_expire'] = \
            str(datetime.datetime.now() + datetime.timedelta(seconds=expire_seconds))
    with open(config_file, 'w') as auth_json_file:
        json.dump(auth_data, auth_json_file)


class DataStoreError(Exception):
    """Base class for exceptions in DataStore class."""
    pass


class CredentialsError(DataStoreError):
    """Exception raised getting credentials from DataStore."""
    pass


class DataStore(object):
    def __init__(self, debug=False):
        self.debug = debug
        self.client_id = None
        self.client_secret = None
        self.user_email = None
        self.refresh_token = None
        self.access_token = None
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
        print('  %s' % oauth2.GeneratePermissionUrl(self.client_id, SCOPE))
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
                                                verbose=self.debug )
        if tmp_token is None or invalid is True:
            raise CredentialsError("File '%s' is missing or invalid!" %
                                        GMAIL_AUTH_TMP)
        self.access_token = tmp_token['access_token']

    def store_access_token(self, token, seconds):
        """Stores an access_token with expiration time
        to a json formatted data file.
        """
        expire_seconds = int(seconds)
        auth_data = {}
        auth_data['access_token'] = token
        auth_data['access_token_expire'] = \
                    str(datetime.datetime.now() +
                    datetime.timedelta(seconds=expire_seconds))
        with open(GMAIL_AUTH_TMP, 'w') as auth_tmp_json_file:
            json.dump(auth_data, auth_tmp_json_file)


def test_configuration():
    """Tries to connect the Gmail SMTP server authenticating
    using the credentials in the GMAIL_AUTH_FILE.
    """
    try:
        ds = DataStore(debug=True)
    except DataStoreError as e:
        print('ERROR:', e)
        print("The file containing Clent Secrets is missing or invalid.")
        print("Register the application on Google Developers Console:")
        print("https://console.developers.google.com")
        print()
        print("Go to Credentials page, download the JSON file")
        print("and rename it as '%s'" % CLIENT_SECRET_FILE)
        return

    try:
        ds.checkin()
    except CredentialsError as e:
        print('ERROR:', e)
        print('Files containing credentials are missing or invalid.')
        print()
        ds.setup()

    print('Done!\n')
    return

    secrets, invalid = get_auth_parms( CLIENT_SECRET_FILE,
                                            'client_id',
                                            'client_secret',
                                            verbose=True )
    if secrets is None or invalid is True:
        print("File containing Clent Secrets '%s' is missing or invalid." %
                                                            CLIENT_SECRET_FILE)
        print("Register the application on Google Developers Console:")
        print("https://console.developers.google.com")
        print()
        print("Go to Credentials page, download the JSON file")
        print("and rename it as '%s'" % CLIENT_SECRET_FILE)
        return

    credentials, invalid = get_auth_parms( GMAIL_AUTH_FILE,
                                            'user_email',
                                            'access_token',
                                            'refresh_token',
                                            verbose=True )
    if credentials is None or invalid is True:
        print('Setup configuration.')
        credentials, invalid = set_oauth_configuration(GMAIL_AUTH_FILE, secrets)
        if credentials is None or invalid is True:
            print('FAIL setting up configuration.')
            return

    print('Test smtp authentication:')
    retcode, retmsg = test_smtp_authentication(
                            credentials['user_email'],
                            oauth2.GenerateOAuth2String(
                                    credentials['user_email'],
                                    credentials['access_token'],
                                    base64_encode=False ),
                            verbose=True )
    print()
    if retcode == 235:
        print('Authentication Succeeded')
    else:
        print('Authentication Failed; retcode (%d): %s' % (retcode, retmsg))

    if retcode == 535:
        # Authentication credentials invalid
        print()
        print('Refreshing the access token...')
        refresh_configuration(GMAIL_AUTH_FILE, secrets)
        print('Retry smtp authentication:')
        credentials, invalid = get_auth_parms( GMAIL_AUTH_FILE,
                                                'user_email',
                                                'access_token',
                                                'refresh_token',
                                                verbose=True )
        retcode, retmsg = test_smtp_authentication(
                                credentials['user_email'],
                                oauth2.GenerateOAuth2String(
                                        credentials['user_email'],
                                        credentials['access_token'],
                                        base64_encode=False ),
                                verbose=True )
        print()
        if retcode == 235:
            print('Retry Authentication Succeeded')
        else:
            print('Retry Authentication Failed; retcode (%d): %s' % (retcode, retmsg))


if __name__ == '__main__':
    test_configuration()
