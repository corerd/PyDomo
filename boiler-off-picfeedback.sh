#!/usr/bin/env bash

# Move to the working directory of the bash script
# See: http://stackoverflow.com/a/246128
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

./camsnapshot.py
usbrelay UWMGH_1=0 2>/dev/null
sleep 3
./camsnapshot.py
./upload.py
