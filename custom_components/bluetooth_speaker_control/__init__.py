from homeassistant.core import HomeAssistant

DOMAIN = "bluetooth_speaker_control"

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Bluetooth Speaker Control integration."""
    hass.states.async_set(f"{DOMAIN}.status", "Initialized")
    return True
