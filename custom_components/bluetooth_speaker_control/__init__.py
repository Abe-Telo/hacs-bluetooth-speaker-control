from homeassistant.core import HomeAssistant, ServiceCall
from .bluetooth import discover_devices, pair_device, connect_device, disconnect_device

DOMAIN = "bluetooth_speaker_control"

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Bluetooth Speaker Control integration."""

    async def handle_pair_speaker(call: ServiceCall):
        """Handle pairing a Bluetooth speaker."""
        mac_address = call.data.get("mac_address")

        # Discover devices and match by MAC address
        devices = discover_devices()
        matched_device = None

        for addr, dev_name in devices:
            if addr == mac_address:
                matched_device = (addr, dev_name)
                break

        if matched_device:
            success = pair_device(matched_device[0])
            if success:
                hass.states.async_set(f"{DOMAIN}.pairing_status", f"Paired with {matched_device[1]} ({matched_device[0]})")
            else:
                hass.states.async_set(f"{DOMAIN}.pairing_status", "Pairing failed")
        else:
            hass.states.async_set(f"{DOMAIN}.pairing_status", "Device not found")

    async def handle_connect_speaker(call: ServiceCall):
        """Handle connecting to a Bluetooth speaker."""
        mac_address = call.data.get("mac_address")
        success = connect_device(mac_address)
        status = "Connected" if success else "Connection failed"
        hass.states.async_set(f"{DOMAIN}.connection_status", status)

    async def handle_disconnect_speaker(call: ServiceCall):
        """Handle disconnecting from a Bluetooth speaker."""
        mac_address = call.data.get("mac_address")
        success = disconnect_device(mac_address)
        status = "Disconnected" if success else "Disconnection failed"
        hass.states.async_set(f"{DOMAIN}.connection_status", status)

    # Register services dynamically
    hass.services.async_register(DOMAIN, "pair_speaker", handle_pair_speaker)
    hass.services.async_register(DOMAIN, "connect_speaker", handle_connect_speaker)
    hass.services.async_register(DOMAIN, "disconnect_speaker", handle_disconnect_speaker)

    return True
