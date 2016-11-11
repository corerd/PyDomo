#!/usr/bin/env bash

# Install Dropbox-Uploader in user HOME .local directory.
# Ref: https://github.com/andreafabrizi/Dropbox-Uploader

TARGET="dropbox_uploader.sh"
DST_DIR="$HOME/.local"

echo "Move to the installation directory $DST_DIR"
cd $DST_DIR

echo "Clone the Dropbox-Uploader repo"
git clone https://github.com/andreafabrizi/Dropbox-Uploader.git

echo "Create symbolic link"
mkdir bin
ln -s "$DST_DIR/Dropbox-Uploader/$TARGET" "$DST_DIR/bin/$TARGET"
