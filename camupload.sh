#!/usr/bin/env bash

./camsnapshot.py
if [ $? -eq 0 ]
then
  ./upload.py
fi
