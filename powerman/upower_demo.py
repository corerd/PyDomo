from __future__ import print_function

from upower import UPowerManager


if __name__ == "__main__":
    pwrMan = UPowerManager()
    battery_device = None
    print('Devices list:')
    for dev in pwrMan.detect_devices():
        print('\t', dev)
        if 'battery' in dev:
            battery_device = dev
    print('Display Devices:\n\t', pwrMan.get_display_device())
    print('Battery Devices:\n\t', battery_device)
    print('Battery State:', pwrMan.get_state(battery_device))
