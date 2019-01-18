#!/usr/bin/env python3
'''
Plot temperature trend of the day grouped by weather services
and upload to dropbox using cloud datastore.

Append to PYTHONPATH the path of the script from which it runs.
Ref. http://stackoverflow.com/a/7886092
'''

from os import path
from datetime import date
from cloud.cloudcfg import getDatastorePath
from boilerctrl.templot import templot
from cloud.upload import main as upload_to_cloud


LOG_FILE_NAME = 'boilerctrl-log.txt'
PLOT_FILE_NAME = 'templot.png'


def run():
    '''Returns status code
    '''
    working_dir = getDatastorePath('cloud/cloudcfg.json')
    log_file_path = path.join(working_dir, LOG_FILE_NAME)
    if path.isfile(log_file_path) is not True:
        print("Log file %s doesn't exist!" % log_file_path)
        return -1
    plot_file_path = path.join(working_dir, PLOT_FILE_NAME)
    plot_day = date.today().strftime('%Y-%m-%d')

    #templot(log_file_path, plot_file_path, '2019-01-17')
    if templot(log_file_path, plot_file_path, plot_day) < 0:
        return -1
    return upload_to_cloud()


if __name__ == "__main__":
    exit(run())
