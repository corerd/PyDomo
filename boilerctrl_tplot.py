#!/usr/bin/env python3
'''Plot the graph of the temperatures checked by boilerctrl.py in one day
and save to dropbox.

Download the temperature log from the boilerctrl dropbox datastore;
plot temperature trend of the previous day grouped by weather services;
upload the plot graph to the same boilerctrl dropbox datastore.

The dropbox datastore has the following directory structure:
    datastore-name
    |-- directory_1
    |   |-- file_1
    |   |-- ...
    |   `-- file_n
    |-- ...
    |-- directory_n
    |   |-- file_1
    |   |-- ...
    |   `-- file_n
    |-- temp-plot-byday
    |   |-- templot_AAAA-MM-DD.png
    |   |-- ...
    |   `-- templot_XXXX-YY-ZZ.png
    |-- file_1
    |-- ...
    |-- file_n
    `-- boilerctrl-log.txt

boilerctrl-log.txt file is generated by boilerctrl.py
The plot graph is uploaded to temp-plot-byday directory.


The MIT License (MIT)

Copyright (c) 2015 Corrado Ubezio

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

# Append to PYTHONPATH the path of the script from which it runs.
# Ref. http://stackoverflow.com/a/7886092

import logging
from datetime import date, timedelta
from os import makedirs, rename
from os.path import dirname, basename, join, realpath, isdir
from sys import argv
from boilerctrl.templot import templot
from cloud.upload import download_datastore, upload_datastore


LOG_FILE_NAME = 'boilerctrl-log.txt'
PLOT_FILE_NAME = 'templot.png'
WORKING_SUB_DIR = 'temp-plot-byday'


def main(argv):
    '''Returns status code
    '''
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        level=logging.DEBUG)
    argc = len(argv)
    if argc != 2:
        print('Sintax: {} <local-datastore>'.format(basename(argv[0]) ))
        return 1
    local_datastore = argv[1]
    working_dir = join(local_datastore, WORKING_SUB_DIR)
    try: 
        makedirs(working_dir)
    except OSError:
        # prevents a duplicated attempt at creating the directory (race condition)
        if not isdir(working_dir):
            logging.error('Unable to create %s working directory' % working_dir)
            return 1
    log_file_path = join(working_dir, LOG_FILE_NAME)
    plot_file_path = join(working_dir, PLOT_FILE_NAME)

    if download_datastore(local_datastore, LOG_FILE_NAME) != 0:
        return 1
    try:
        rename(join(local_datastore, LOG_FILE_NAME), log_file_path)
    except:
        logging.error('Unable to move %s to %s' % (LOG_FILE_NAME, working_dir))
        return 1

    plot_day = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    if templot(log_file_path, plot_file_path, plot_day) != 0:
        logging.info('Nothing to plot at %s' % plot_day)
        return 1

    return upload_datastore(local_datastore)


if __name__ == "__main__":
    exit(main(argv))
