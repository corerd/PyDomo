#!/usr/bin/env python
#
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


import logging
from os import remove, rmdir, walk, makedirs
from os.path import dirname, join, realpath, split, isdir
from utils.cli import cfg_file_arg
from cloud.cloudcfg import ConfigDataLoad
from cloud.dropboxsrv import dropbox_file_xfer


# Globals
VERSION = '1.0'
DEFAULT_CFG_FILE = 'cloudcfg.json'

DEFAULT_CFG_FILE_PATH = join(dirname(realpath(__file__)), DEFAULT_CFG_FILE)

USAGE = '''Upload the local datastore to a cloud service.

Datastore directory structure:
    datastore-name
    |-- directory_1 (volatile)
    |   |-- file_1
    |   |-- ...
    |   `-- file_n
    |-- ...
    |-- directory_n (volatile)
    |   |-- file_1
    |   |-- ...
    |   `-- file_n
    |-- file_1 (persistent)
    |-- ...
    `-- file_n (persistent)

Each file direct son of the root datastore-name is "persistent".
Any other sub-directories and files are "volatile".

If a member is "volatile", it will be removed after succesfull uploaded.
Otherwise it will remain stored.

The datastore path is taken from a configuration file in JSON format.
If none given, the configuration is read from the file:
    %s
''' % DEFAULT_CFG_FILE_PATH


def upload_files(local_dirpath, filelist, remote_datastore_name, persistent):
    local_remove = False
    for filename in filelist:
        remote_dirpath = remote_datastore_name
        (_, tail) = split(local_dirpath)
        if tail != remote_datastore_name:
            remote_dirpath = join(remote_dirpath, tail)
        remote_filepath = join(remote_dirpath, filename)
        local_filepath = join(local_dirpath, filename)
        local_remove = dropbox_file_xfer('upload', local_filepath, remote_filepath)
        if persistent is False:
            if local_remove is True:
                logging.info('Remove %s' % local_filepath)
                remove(local_filepath)


def upload_datastore(local_datastore_path_name):
    persistent = True
    (_, datastore_name) = split(local_datastore_path_name)
    for (dirpath, dirnames, filenames) in \
                                walk(local_datastore_path_name, topdown=True):
        # The triple for a directory is generated before
        # the triples for any of its subdirectories
        # (directories are generated top-down).
        if len(dirnames) == 0 and len(filenames) == 0:
            # dirpath is empty.
            if persistent is False:
                logging.info('remove directory %s' % dirpath)
                rmdir(dirpath)
        else:
            upload_files(dirpath, filenames, datastore_name, persistent)
        persistent = False
    return 0


def download_datastore(local_datastore_path_name, filepath):
    try: 
        makedirs(local_datastore_path_name)
    except OSError:
        # prevents a duplicated attempt at creating the directory (race condition)
        if not isdir(local_datastore_path_name):
            logging.error('Unable to create %s directory' % local_datastore_path_name)
            return 1
    (_, datastore_name) = split(local_datastore_path_name)
    local_filepath = join(local_datastore_path_name, filepath)
    remote_filepath = join(datastore_name, filepath)
    if dropbox_file_xfer('download', local_filepath, remote_filepath) is not True:
        return 1
    return 0


def get_config(cfg_file_path):
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        level=logging.DEBUG)

    options = cfg_file_arg(VERSION, USAGE, cfg_file_path)
    logging.info('Read configuration from file: %s' % options.cfg_file)

    cfg_data = None
    try:
        cfg_data = ConfigDataLoad(options.cfg_file)
    except:
        logging.error('Unable to load config')
    return cfg_data


def cloud_download(cloud_cfg_file_path, remote_filename):
    cfg_data = get_config(cloud_cfg_file_path)
    if cfg_data == None:
        return 1
    return download_datastore(cfg_data.data['datastore'], remote_filename)


def cloud_upload(cloud_cfg_file_path):
    cfg_data = get_config(cloud_cfg_file_path)
    if cfg_data == None:
        return 1
    return upload_datastore(cfg_data.data['datastore'])


def main():
    return cloud_upload(DEFAULT_CFG_FILE_PATH)


if __name__ == "__main__":
    exit(main())
