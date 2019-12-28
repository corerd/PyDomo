from __future__ import print_function

from upower import UPowerManager


if __name__ == "__main__":
    pwrMan = UPowerManager()
    print('Devices list:')
    for dev in pwrMan.detect_devices():
        print('\t', dev)
    print('On battery:', pwrMan.on_battery())
