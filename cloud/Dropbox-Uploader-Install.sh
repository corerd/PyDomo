#!/usr/bin/env bash

TARGET="dropbox_uploader.sh"
DST_DIR="$HOME/.local/opt"
SYMLINK_DIR="/usr/local/bin"
EXIT_CODE=0

echo "Install Dropbox-Uploader in user $DST_DIR"
echo "Ref: https://github.com/andreafabrizi/Dropbox-Uploader"
echo

if [ ! -d "$DST_DIR" ]; then
    echo "Create $DST_DIR"
    mkdir -p $DST_DIR
fi

echo "Move to the installation directory $DST_DIR"
if ! pushd $DST_DIR; then
    exit 1
fi

echo "Clone the Dropbox-Uploader repository"
git clone https://github.com/andreafabrizi/Dropbox-Uploader.git
EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
    echo "Create symbolic link to $TARGET in $SYMLINK_DIR"
    sudo ln -s "$DST_DIR/Dropbox-Uploader/$TARGET" "$SYMLINK_DIR/$TARGET"
    EXIT_CODE=$?
fi

echo "Leave $DST_DIR"
popd
exit $EXIT_CODE
