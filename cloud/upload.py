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


from os import remove, rmdir, walk
from os.path import dirname, join, realpath, split


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
    print 'Persistent:', persistent
    local_remove = False
    for filename in filelist:
        remote_dirpath = remote_datastore_name
        (head, tail) = split(local_dirpath)
        if tail != remote_datastore_name:
            remote_dirpath = join(remote_dirpath, tail)
        remote_filepath = join(remote_dirpath, filename)
        local_filepath = join(local_dirpath, filename)
        print 'Upload', local_filepath
        print '--> to', remote_filepath
        if persistent is False:
            if local_remove is True:
                print 'Remove', local_filepath
                remove(local_filepath)


def upload_datastore(local_datastore_path_name):
    persistent = True
    (local_datastore_path, datastore_name) = split(local_datastore_path_name)
    for (dirpath, dirnames, filenames) in \
                                walk(local_datastore_path_name, topdown=True):
        # The triple for a directory is generated before
        # the triples for any of its subdirectories
        # (directories are generated top-down).
        if len(dirnames) == 0 and len(filenames) == 0:
            # dirpath is empty.
            if persistent is False:
                print 'remove directory', dirpath
                rmdir(dirpath)
        else:
            upload_files(dirpath, filenames, datastore_name, persistent)
        persistent = False
    return 0


def main():
    from utils.cli import cfg_file_arg
    from cloudcfg import ConfigDataLoad

    options = cfg_file_arg(VERSION, USAGE, DEFAULT_CFG_FILE_PATH)
    print 'Read configuration from file:', options.cfg_file

    try:
        cfg_data = ConfigDataLoad(options.cfg_file)
    except:
        print 'Unable to load config'
        return 1

    return upload_datastore(cfg_data.data['datastore'])


if __name__ == "__main__":
    exit(main())
