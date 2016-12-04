#!/usr/bin/env bash

DATASTOREPATH="$(./cloudDatastore.py)"
if [ ${#DATASTOREPATH} -eq 0 ]; then
  echo "ERROR: undefined datastore"
  exit 1
fi

if [ ! -d "$DATASTOREPATH" ]; then
  # Create directory
  mkdir -p "$DATASTOREPATH"
fi

if [ -f "$DATASTOREPATH/temperature.txt" ]; then
  cat "$DATASTOREPATH/temperature.txt"
fi
while true; do
  ./weather.py > "$DATASTOREPATH/weatherlog.txt" 2>&1
  tail -1 "$DATASTOREPATH/temperature.txt"
  sleep 30m
done
