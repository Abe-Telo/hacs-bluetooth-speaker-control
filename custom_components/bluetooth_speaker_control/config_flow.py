from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, DEFAULT_NAME
from .bluetooth import discover_bluetooth_devices
import logging

_LOGGER = logging.getLogger(__name__)

class BluetoothSpeakerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the configuration flow for Bluetooth Speaker Control."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            # Save the selected device and create the configuration entry
            return self.async_create_entry(
                title=f"{user_input['device_name']} ({user_input['mac_address']})",
                data=user_input,
            )

        # Discover devices using Home Assistant's Bluetooth integration
        devices = await discover_bluetooth_devices(self.hass)

        if not devices:
            return self.async_show_form(
                step_id="user",
                errors={"base": "no_devices_found"}
            )

        # Display the configuration form with discovered devices
        return self.async_show_form(
            step_id="user",
            data_schema=self._get_schema(devices)
        )

    @callback
    def _get_schema(self, devices):
        """Generate the schema with discovered devices."""
        from homeassistant.helpers.selector import SelectSelector, SelectSelectorConfig

        options = {
            f"{device['name']} ({device['mac']})": device['mac'] for device in devices
        }

        return {
            "device_name": SelectSelector(
                SelectSelectorConfig(
                    options=list(options.keys()),
                    mode="dropdown"
                )
            ),
            "mac_address": SelectSelector(
                SelectSelectorConfig(
                    options=list(options.values()),
                    mode="dropdown"
                )
            ),
        }
