#!/bin/sh

# Check if the AC laptop adapter is plugged or not
# See: https://askubuntu.com/a/386953
#
# Instead of checking for AC adapter (not working on my architecture)
# check for battery status

battery_status=$(acpi -b | cut -d' ' -f3 | cut -d, -f1)
if [ "$battery_status" = "Discharging" ]; then
    echo "The AC Adapter is OFF"
else
    echo "The AC Adapter is ON"
fi
