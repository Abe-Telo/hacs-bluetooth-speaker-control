import bluetooth

def discover_devices():
    """Discover nearby Bluetooth devices."""
    devices = bluetooth.discover_devices(lookup_names=True)
    return devices

def connect_to_device(device_mac):
    """Connect to a Bluetooth device."""
    # Add connection logic using pybluez or similar
    pass
