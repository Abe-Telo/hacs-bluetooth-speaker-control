from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.selector import SelectSelector, SelectSelectorConfig
from .const import DOMAIN, DEFAULT_NAME
import bluetooth  # Using pybluez for discovery

class BluetoothSpeakerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Bluetooth Speaker Control."""

    VERSION = 1

    def __init__(self):
        self.devices = []

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            # Validate user input here and create the configuration entry
            return self.async_create_entry(
                title=user_input.get("name", DEFAULT_NAME),
                data=user_input,
            )

        # Discover devices and populate self.devices
        self.devices = await self.hass.async_add_executor_job(self.discover_bluetooth_devices)

        if not self.devices:
            # No devices found, show an error
            return self.async_show_form(
                step_id="user",
                errors={"base": "no_devices_found"},
                data_schema=self._get_schema()
            )

        # Show the form with the device selection
        return self.async_show_form(
            step_id="user",
            data_schema=self._get_schema()
        )

    def discover_bluetooth_devices(self):
        """Discover nearby Bluetooth devices."""
        try:
            devices = bluetooth.discover_devices(lookup_names=True)
            return [(addr, name) for addr, name in devices]
        except Exception as e:
            self.hass.logger.error(f"Error discovering Bluetooth devices: {e}")
            return []

    @staticmethod
    @callback
    def _get_schema():
        """Return the schema for the setup form."""
        device_options = {
            f"{addr} ({name})": addr for addr, name in self.devices
        }

        return {
            "name": SelectSelector(SelectSelectorConfig(options=list(device_options.keys()))),
            "mac_address": SelectSelector(SelectSelectorConfig(options=list(device_options.values()))),
        }
