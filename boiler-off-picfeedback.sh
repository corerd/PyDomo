#!/usr/bin/env bash

./camsnapshot.py
usbrelay UWMGH_1=0 2>/dev/null
sleep 3
./camsnapshot.py
./upload.py
