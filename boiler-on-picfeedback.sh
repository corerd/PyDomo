#!/usr/bin/env bash

./camsnapshot.py
usbrelay UWMGH_1=1 2>/dev/null
sleep 3
./camsnapshot.py
./upload.py
