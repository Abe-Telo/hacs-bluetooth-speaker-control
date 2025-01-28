from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN
from .bluetooth import discover_bluetooth_devices
from homeassistant.helpers.selector import TextSelector, TextSelectorConfig
import logging

_LOGGER = logging.getLogger(__name__)


class BluetoothSpeakerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the configuration flow for Bluetooth Speaker Control."""

    VERSION = 1

    def __init__(self):
        self.discovered_devices = []
        self.selected_device = None

    async def async_step_user(self, user_input=None):
        """Handle the initial step: list all devices with a refresh button."""
        if user_input is not None:
            # If 'refresh' is clicked, refresh device discovery
            if user_input.get("refresh") == "refresh":
                _LOGGER.debug("Refreshing Bluetooth device list.")
                return await self.async_step_user()

            # User selected a device, proceed to naming step
            selected_mac = user_input.get("mac_address")
            self.selected_device = next(
                (device for device in self.discovered_devices if device["mac"] == selected_mac),
                None,
            )
            if self.selected_device:
                return await self.async_step_set_name()

            # If no valid selection is found, show error
            _LOGGER.error("Invalid selection. Device not found.")
            return self.async_show_form(
                step_id="user",
                errors={"base": "invalid_selection"},
                data_schema=self._get_schema(),
            )

        # Initial device discovery
        self.discovered_devices = await discover_bluetooth_devices(self.hass)

        if not self.discovered_devices:
            _LOGGER.warning("No Bluetooth devices discovered.")
            return self.async_show_form(
                step_id="user",
                errors={"base": "no_devices_found"},
                data_schema=self._get_schema(),
            )

        # Show the list of discovered devices
        return self.async_show_form(
            step_id="user",
            data_schema=self._get_schema(),
        )

    async def async_step_set_name(self, user_input=None):
        """Step to ask the user for a name for the selected device."""
        if user_input is not None:
            return self.async_create_entry(
                title=user_input["device_name"],
                data={
                    "device_name": user_input["device_name"],
                    "mac_address": self.selected_device["mac"],
                },
            )

        # Show form for entering the name
        data_schema = {
            "device_name": TextSelector(TextSelectorConfig(type="text")),
            "mac_address": TextSelector(
                TextSelectorConfig(type="text", default=self.selected_device["mac"])
            ),
        }

        return self.async_show_form(
            step_id="set_name",
            data_schema=data_schema,
        )

    @callback
    def _get_schema(self):
        """Generate schema for the user step."""
        from homeassistant.helpers.selector import SelectSelector, SelectSelectorConfig

        options = {device["mac"]: f"{device['name']} ({device['mac']})" for device in self.discovered_devices}

        # Add a "Refresh" option to the schema
        return {
            "mac_address": SelectSelector(
                SelectSelectorConfig(
                    options=[{"value": k, "label": v} for k, v in options.items()],
                    mode="dropdown",
                )
            ),
            "refresh": TextSelector(
                TextSelectorConfig(type="text", default="refresh")
            ),
        }
