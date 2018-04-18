#!/bin/sh

# Check if the AC laptop adapter is plugged or not
# See: https://askubuntu.com/a/386953
#
# Instead of checking for AC adapter (not working on my architecture)
# check for battery status

#battery_status=$(acpi -b | cut -d' ' -f3 | cut -d, -f1)
battery_status=$(acpi -b)
if [ $? -ne 0 ]; then
    exit 1
fi
battery_status=$(echo $battery_status | cut -d' ' -f3 | cut -d, -f1)
if [ "$battery_status" = "" ]; then
    echo "No battery informations" 1>&2
    exit 2
fi
if [ "$battery_status" = "Discharging" ]; then
    echo "The AC Adapter is OFF"
else
    echo "The AC Adapter is ON"
fi
