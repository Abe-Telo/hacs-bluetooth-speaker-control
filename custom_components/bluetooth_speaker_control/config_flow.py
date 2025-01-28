from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN
from .bluetooth import discover_bluetooth_devices
import logging

_LOGGER = logging.getLogger(__name__)


class BluetoothSpeakerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the configuration flow for Bluetooth Speaker Control."""

    VERSION = 1

    def __init__(self):
        self.discovered_devices = []
        self.selected_device = None

    async def async_step_user(self, user_input=None):
        """Handle the initial step: list available devices with a refresh option."""
        if user_input is not None:
            # Handle refresh request
            if user_input.get("refresh"):
                _LOGGER.debug("Refreshing Bluetooth device list.")
                self.discovered_devices = await discover_bluetooth_devices(self.hass)
                return await self.async_step_user()

            # Handle device selection
            selected_mac = user_input.get("device_mac")
            self.selected_device = next(
                (device for device in self.discovered_devices if device["mac"] == selected_mac),
                None,
            )
            if self.selected_device:
                return await self.async_step_set_name()

            # Invalid selection
            _LOGGER.error("Invalid selection. Device not found.")
            return self.async_show_form(
                step_id="user",
                errors={"base": "invalid_selection"},
            )

        # Initial discovery of devices
        self.discovered_devices = await discover_bluetooth_devices(self.hass)

        if not self.discovered_devices:
            _LOGGER.warning("No devices discovered.")
            return self.async_show_form(
                step_id="user",
                errors={"base": "no_devices_found"},
                data_schema=self._get_device_schema(no_devices=True),
            )

        return self.async_show_form(
            step_id="user",
            data_schema=self._get_device_schema(),
        )

    async def async_step_set_name(self, user_input=None):
        """Ask the user to set a custom name for the selected device."""
        if user_input is not None:
            # Save the selected device and create the configuration entry
            return self.async_create_entry(
                title=user_input["device_name"],
                data={
                    "device_name": user_input["device_name"],
                    "mac_address": self.selected_device["mac"],
                },
            )

        # Show the naming form
        return self.async_show_form(
            step_id="set_name",
            data_schema={
                "device_name": str,
            },
        )

    @callback
    def _get_device_schema(self, no_devices=False):
        """Generate schema for the list of devices or refresh option."""
        if no_devices:
            # No devices: Show only a refresh button
            return {
                "refresh": bool,
            }

        # Devices found: List devices with a refresh option
        options = {
            device["mac"]: f"{device['name']} ({device['mac']})" for device in self.discovered_devices
        }
        schema = {
            "device_mac": config_entries.CONF_SELECT(options),
            "refresh": bool,
        }
        return schema
