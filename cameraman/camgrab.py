#!/usr/bin/env python

# The MIT License (MIT)
#
# Copyright (c) 2015 Corrado Ubezio
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Capturing a single image from webcam

In Linux there are the following methods:

METHOD 1: RTSP protocol
avconv -i rtsp://<user>:<pass>@<local_ip>:<port>/video.mjpg -vframes 1 -r 1 -s 640x480 image.jpg

METHOD 2: HTTP protocol
avconv -i http://<user>:<pass>@<local_ip>:<port>/video.mjpg -vframes 1 -r 1 -s 640x480 image.jpg

METHOD 3: If the camera is smart enough, it is possible to send an http request to take a snapshot
wget --tries=2 --timeout=10 http://<user>:<pass>@<local_ip>:<port>/cgi-bin/jpg/image -O snapshot.jpg

See also: Link: http://stackoverflow.com/a/11094891
"""

from __future__ import print_function

from requests import get, post
from time import sleep
from sys import stderr


'''In dark image detection, compare 'light' pixels with 'dark' ones.'''
LIGHT_THRESHOLD_DEFAULT = -1


def cv2_gshistogram(imageAsByteArray):
    '''Use OpenCV tp convert the bytearray image buffer to grayscale and
    returns the histogram as a list of pixel counts,
    one for each pixel value in the source image.

    Since the source image has been converted to one only band (grayscale),
    there are 256 pixel counts, that is an index for each shade of grey.
    '''
    from cv2 import calcHist, imdecode, IMREAD_GRAYSCALE
    from numpy import frombuffer, uint8

    img = frombuffer(imageAsByteArray, dtype=uint8)
    grayimg = imdecode(img, IMREAD_GRAYSCALE)
    return calcHist([grayimg],[0],None,[256],[0,256])


def pil_gshistogram(imageAsByteArray):
    '''Use Pillow tp convert the bytearray image buffer to grayscale and
    returns the histogram as a list of pixel counts,
    one for each pixel value in the source image.

    Since the source image has been converted to one only band (grayscale),
    there are 256 pixel counts, that is an index for each shade of grey.
    '''
    from PIL import Image
    import StringIO

    # Convert the bytes object containing a jpeg image to Pillow
    # see: https://stackoverflow.com/a/24997383
    img = Image.open(StringIO.StringIO(imageAsByteArray))

    # Convert to greyscale and return the pixel counts list
    grayimg = img.convert(mode='L')
    return grayimg.histogram()


def isDarkImage(imageAsBytearray, lightThreshold=LIGHT_THRESHOLD_DEFAULT):
    '''Return True if in the grayscale histogram of the image there are
    less 'light' pixels than 'dark' ones.
    If lightThreshold is supplied then 'light' pixels are compared with it.

    # In a grayscale histogram, the first 128 values are 'dark',
    # the last 128 are 'light' pixels.
    See: https://stackoverflow.com/a/8659785
    '''
    pixel_counts = pil_gshistogram(imageAsBytearray)
    indexes = len(pixel_counts)  # should be 256 (an index for each shade of grey)
    light_pixels = sum(pixel_counts[indexes/2:])
    if lightThreshold <= LIGHT_THRESHOLD_DEFAULT:
        lightThreshold = sum(pixel_counts[:indexes/2])  # dark pixels
    if light_pixels <= lightThreshold:
        return True
    return False


def lightsIP(cameraUrl, username, password, switchOn):
    '''Switch IR leds on/off
    See night vision mode on/off for D-Link DCS-932L IP Camera
    link: http://forums.ispyconnect.com/forum.aspx?g=posts&t=1151

    Returns bool
    '''
    if switchOn is True:
        payload = {"IRLed":"1"}
    else:
        payload = {"IRLed":"0"}
    try:
        r = post(cameraUrl, auth=(username, password),  data=payload)
    except Exception:
        # TODO: better to handle exceptions as in:
        # http://docs.python-requests.org/en/latest/user/quickstart/#errors-and-exceptions
        return False
    if r.status_code == 204:
        '''The server has successfully fulfilled the request
        and there is no additional content.
        '''
        return True
    return False


def grabImageFromIP(cameraUrl, username, password):
    '''Grabs a snapshot from the IP camera referenced by its URL.
    See: http://stackoverflow.com/a/13137873

    Returns bool, JPEG bytearray.
    '''
    try:
        r = get(cameraUrl, auth=(username, password), timeout=10, stream=True)
    except Exception:
        # TODO: better to handle exceptions as in:
        # http://docs.python-requests.org/en/latest/user/quickstart/#errors-and-exceptions
        return False, None
    if r.status_code != 200:
        return False, None
    jpgImage = b""
    for chunk in r.iter_content(1024):
        jpgImage = jpgImage + chunk
    if len(jpgImage) == 0:
        return False, None
    return True, jpgImage


def grabImageFromUSB(cameraNumber=0):
    '''Grabs a snapshot from the specified USB camera.

    Returns bool, video frame decoded as a JPEG bytearray.
    '''
    from cv2 import VideoCapture, imencode

    # initialize the camera
    cam = VideoCapture(cameraNumber)
    retVal, rawData = cam.read()
    if not retVal:
        # frame captured returns errors
        return False, None
    retVal, jpgData = imencode('.jpg', rawData)
    if not retVal:
        # image encode errors
        return False, None
    return retVal, bytearray(jpgData)


def grabImage(cameraDesc):
    '''Wraps grabImageFromIP and grabImageFromUSB
    The camera type (usb or ip) is get from the descriptor.

    Returns bool, JPEG bytearray.
    '''
    retval = False
    jpgImage = b""
    camProtAndAddr = cameraDesc['source'].split('://')
    if camProtAndAddr[0] == 'usb':
        retval, jpgImage = grabImageFromUSB(eval(camProtAndAddr[1]))
    elif camProtAndAddr[0] == 'http':
        retval, jpgImage = grabImageFromIP(cameraDesc['source'],
                        cameraDesc['optional-auth']['user-name'],
                        cameraDesc['optional-auth']['password'])
    return retval, jpgImage


def imageCapture(cameraDesc, imageFileName):
    '''Saves a snapshot from a camera to the specified file.
    If camera has night vision capability, check the quality of the image
    and shot again with IrLeds ON if it is too dark.

    The camera type (usb or ip) is get from the descriptor:
    cameraDesc = {
        "optional-irled": {
            "url-ctrl" : "<camera_irled_ctrl_protocol_and_address>",
            "opt-light-threshold" : "<threshold_light_pixels>"
        },
        "optional-auth": {
            "user-name" : "<camera_user>",
            "password": "<camera_user_password>"
        },
        "source":  "<camera_protocol_and_address>"
    }

    Returns bool
    '''
    retVal, jpgImage = grabImage(cameraDesc)
    if not retVal:
        # grabImage returns errors
        return False

    '''If camera has night vision capability, check the quality of the image
    and shot again with IrLeds ON if it is too dark'''
    try:
         irLed_ctrl_url = cameraDesc['optional-irled']['url-ctrl']
         capabilityNightVision = True
    except KeyError:
        capabilityNightVision = False
    if capabilityNightVision is True:
        try:
            threshold = cameraDesc['optional-irled']['opt-light-threshold']
            threshold = int(threshold)
        except (KeyError, ValueError):
            threshold = LIGHT_THRESHOLD_DEFAULT
        print('NightVision capability is True; threshold=%d' % threshold, file=stderr)
        if isDarkImage(jpgImage, threshold):
            try:
                username = cameraDesc['optional-auth']['user-name']
                password = cameraDesc['optional-auth']['password']
            except KeyError:
                username = ''
                password = ''
            print('Recover a Dark Image', file=stderr)
            #print('Connect <%s>:<%s>@%s' % (username, password, irLed_ctrl_url), file=stderr)
            irLedOk = lightsIP(irLed_ctrl_url, username, password, True)
            if irLedOk is False:
                # TODO check the result
                print('FAIL to switch IrLeds ON', file=stderr)
            else:
                # wait for IrLeds settling
                sleep(4)
            grabOk, jpgImage = grabImage(cameraDesc)
            irLedOk = lightsIP(irLed_ctrl_url, username, password, False)
            if irLedOk is False:
                # TODO check the result
                print('FAIL to switch IrLeds OFF', file=stderr)
            if grabOk is False:
                # grabImage returns errors
                return False

    try:
        with open(imageFileName, 'wb') as f:
            f.write(jpgImage)
    except IOError:
        retVal = False
    return retVal


if __name__ == "__main__":
    pass
