from homeassistant.components.bluetooth import async_get_scanner
import logging
import json

_LOGGER = logging.getLogger(__name__)

async def discover_bluetooth_devices(hass):
    """Discover nearby Bluetooth devices using Home Assistant's Bluetooth integration."""
    try:
        # Get the Bluetooth scanner
        scanner = async_get_scanner(hass)
        if not scanner:
            _LOGGER.error("❌ Bluetooth scanner unavailable. Ensure the Bluetooth integration is set up correctly.")
            return []

        # Attempt to use discovered_devices_and_advertisement_data if available
        discovered_devices = getattr(scanner, "discovered_devices_and_advertisement_data", None)

        if not discovered_devices:
            _LOGGER.warning("⚠️ No advertisement data found. Using fallback to scanner.discovered_devices.")
            discovered_devices = {
                device: {"rssi": getattr(device, "rssi", -100)}  # Add at least RSSI
                for device in getattr(scanner, "discovered_devices", [])
            }

        if not discovered_devices:
            _LOGGER.warning(
                "⚠️ No Bluetooth devices discovered. Ensure devices are in discoverable mode and within range."
            )
            return []

        device_list = []

        _LOGGER.info(f"🔍 Found {len(discovered_devices)} Bluetooth devices.")

        for device, adv_data in discovered_devices.items():
            try:
                # Process the device and advertisement data
                device_data = {
                    **extract_ble_device(device),
                    **extract_adv_data(adv_data),
                }
                device_list.append(device_data)

                # Log the discovered device for debugging
                _LOGGER.debug("📡 Device discovered: %s", json.dumps(device_data, indent=4))

            except Exception as e:
                _LOGGER.error(f"⚠️ Error processing device {device}: {e}")

        return device_list

    except Exception as e:
        _LOGGER.error(f"🔥 Error during Bluetooth discovery: {e}")
        return []


def extract_adv_data(adv_data):
    """Extract attributes from AdvertisementData safely."""
    if adv_data is None:
        return {
            "local_name": "Unknown",
            "manufacturer": "Unknown",
            "service_uuids": [],
            "service_data": {},
            "manufacturer_data": {},
            "rssi": -100,  # Dummy RSSI value
            "tx_power": "Unknown",
        }

    return {
        "local_name": getattr(adv_data, "local_name", "Unknown"),
        "manufacturer": getattr(adv_data, "manufacturer", "Unknown"),
        "service_uuids": getattr(adv_data, "service_uuids", []),
        "service_data": _serialize_bytes(getattr(adv_data, "service_data", {})),
        "manufacturer_data": _serialize_bytes(getattr(adv_data, "manufacturer_data", {})),
        "rssi": getattr(adv_data, "rssi", -100),  # Use RSSI from AdvertisementData
        "tx_power": getattr(adv_data, "tx_power", "Unknown"),
    }


def extract_ble_device(device):
    """Extract attributes from BLEDevice safely."""
    return {
        "name": getattr(device, "name", "Unknown"),
        "mac": getattr(device, "address", "Unknown"),
        "details": str(getattr(device, "details", {})),
        "id": getattr(device, "id", "Unknown"),
    }


def _serialize_bytes(data):
    """Convert bytearray or bytes to JSON serializable format."""
    if isinstance(data, (bytes, bytearray)):
        return list(data)  # Convert bytearray to a list of integers
    elif isinstance(data, dict):
        return {key: _serialize_bytes(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [_serialize_bytes(item) for item in data]
    return data






# --- 🔗 Real Pairing, Connecting, Disconnecting using Bleak ---

async def pair_device(mac_address):
    """Attempt to pair with a Bluetooth device."""
    try:
        _LOGGER.info(f"🔗 Attempting to pair with {mac_address}...")
        devices = await BleakScanner.discover()
        device = next((d for d in devices if d.address.lower() == mac_address.lower()), None)

        if device is None:
            _LOGGER.error(f"❌ Device {mac_address} not found. Ensure it's discoverable.")
            return False

        async with BleakClient(device.address) as client:
            if client.is_connected:
                _LOGGER.info(f"✅ Successfully paired with {mac_address}")
                return True
            else:
                _LOGGER.error(f"❌ Pairing failed for {mac_address}")
                return False
    except BleakError as e:
        _LOGGER.error(f"⚠️ Bluetooth error during pairing: {e}")
        return False

async def connect_device(mac_address):
    """Attempt to connect to a Bluetooth device."""
    try:
        _LOGGER.info(f"🔄 Attempting to connect to {mac_address}...")
        async with BleakClient(mac_address) as client:
            await client.connect()
            if client.is_connected:
                _LOGGER.info(f"✅ Connected to {mac_address}")
                return True
            else:
                _LOGGER.error(f"❌ Connection failed for {mac_address}")
                return False
    except BleakError as e:
        _LOGGER.error(f"⚠️ Bluetooth error during connection: {e}")
        return False

async def disconnect_device(mac_address):
    """Attempt to disconnect from a Bluetooth device."""
    try:
        _LOGGER.info(f"🔌 Attempting to disconnect from {mac_address}...")
        async with BleakClient(mac_address) as client:
            await client.disconnect()
            _LOGGER.info(f"✅ Disconnected from {mac_address}")
            return True
    except BleakError as e:
        _LOGGER.error(f"⚠️ Bluetooth error during disconnection: {e}")
        return False
