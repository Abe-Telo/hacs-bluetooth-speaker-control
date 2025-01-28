from homeassistant.core import HomeAssistant, ServiceCall
from .bluetooth import discover_devices, pair_device

DOMAIN = "bluetooth_speaker_control"

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Bluetooth Speaker Control integration."""

    async def handle_pair_speaker(call: ServiceCall):
        """Handle pairing a Bluetooth speaker."""
        name = call.data.get("name")
        mac_address = call.data.get("mac_address")

        # Discover devices and match by name or MAC address
        devices = discover_devices()
        matched_device = None

        for addr, dev_name in devices:
            if dev_name == name or addr == mac_address:
                matched_device = (addr, dev_name)
                break

        if matched_device:
            success = pair_device(matched_device[0])
            if success:
                hass.states.async_set(f"{DOMAIN}.pairing_status", "Paired successfully")
            else:
                hass.states.async_set(f"{DOMAIN}.pairing_status", "Pairing failed")
        else:
            hass.states.async_set(f"{DOMAIN}.pairing_status", "Device not found")

    # Register service
    hass.services.async_register(DOMAIN, "pair_speaker", handle_pair_speaker)

    return True


