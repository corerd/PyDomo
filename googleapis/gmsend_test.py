#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Command-line application to send email message from the user's Gmail account
by means of gmailapi.py library
"""

from __future__ import print_function

import logging
import traceback
from sys import argv, version_info
from datetime import datetime
from random import randint

from apiclient import errors

from gmailapi import gmSend


TEST_SUBJECT = 'Python {pymajor}.{pyminor} !?gmsend test¿¡ at {now}' 
TEST_MESSAGE = """Send an email using Gmail API from Python
with some unicode charaters in the subject
and in the text body à è é ì ò ù
adding random content {}
"""


def gmsend_test(to, attachment=None):
    """Send the email TEST_MESSAGE from the user's account

    Args:
        to: Email address of the receiver.
        attachment: The path to the file to be attached.

    This is an attended command-line application, then set modeIsInteractive
    to True allowing the gmSend() function, if required, to open a browser to
    start the user consent process.
    """
    subject = TEST_SUBJECT.format( pymajor=version_info.major,
                                    pyminor=version_info.minor,
                                    now=datetime.now() )
    text = TEST_MESSAGE.format(randint(100, 999))
    if attachment:
        text = text + 'with attachment'
    try:
        message = gmSend(to, subject, text, attachment, modeIsInteractive=True)
    except errors.HttpError as e:
        logging.error('HttpError occurred: %s' % e)
    except Exception:
        logging.error(traceback.format_exc())
    else:
        print('SUCCEEDED: Message Sent Id: %s' % message['id'])


def main():
    print('Python {}.{}.{}'.format(version_info.major, version_info.minor,
                                    version_info.micro))
    print('Send a test unicode email message from the user Gmail account')
    if len(argv) < 2 or len(argv) > 3:
        print('USAGE; gmsend_test.py <dest-address> [attached-file-path]')
        return
    dest_address = argv[1]
    if len(argv) == 3:
        attached = argv[2]
    else:
        attached = None
    gmsend_test(dest_address, attached)


if __name__ == '__main__':
    main()
