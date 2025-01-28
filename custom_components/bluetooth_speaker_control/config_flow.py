from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN
from .bluetooth import discover_bluetooth_devices
from homeassistant.helpers.selector import SelectSelector, SelectSelectorConfig, TextSelector, TextSelectorConfig
import logging

_LOGGER = logging.getLogger(__name__)


class BluetoothSpeakerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the configuration flow for Bluetooth Speaker Control."""

    VERSION = 1

    def __init__(self):
        self.discovered_devices = []
        self.selected_device = None

    async def async_step_user(self, user_input=None):
        """Handle the initial step: list devices and provide a refresh option."""
        if user_input is not None:
            # If refresh is clicked, rediscover devices
            if user_input.get("refresh"):
                _LOGGER.debug("Refreshing Bluetooth device list.")
                self.discovered_devices = await discover_bluetooth_devices(self.hass)
                return await self.async_step_user()

            # User selected a device, proceed to naming step
            selected_mac = user_input.get("mac_address")
            self.selected_device = next(
                (device for device in self.discovered_devices if device["mac"] == selected_mac),
                None,
            )
            if self.selected_device:
                return await self.async_step_set_name()

            # Invalid selection
            _LOGGER.error("Invalid device selection.")
            return self.async_show_form(
                step_id="user",
                data_schema=self._get_schema(),
                errors={"base": "invalid_selection"},
            )

        # Discover devices on the initial load
        self.discovered_devices = await discover_bluetooth_devices(self.hass)

        if not self.discovered_devices:
            _LOGGER.warning("No devices discovered.")
            return self.async_show_form(
                step_id="user",
                data_schema=self._get_schema(),
                errors={"base": "no_devices_found"},
            )

        return self.async_show_form(
            step_id="user",
            data_schema=self._get_schema(),
        )

    async def async_step_set_name(self, user_input=None):
        """Step to ask for a custom name for the selected device."""
        if user_input is not None:
            # Create the configuration entry
            return self.async_create_entry(
                title=user_input["device_name"],
                data={
                    "device_name": user_input["device_name"],
                    "mac_address": self.selected_device["mac"],
                },
            )

        # Display form to set the device name
        data_schema = {
            "device_name": TextSelector(TextSelectorConfig(type="text")),
        }

        return self.async_show_form(
            step_id="set_name",
            data_schema=data_schema,
            description_placeholders={
                "mac_address": self.selected_device["mac"],
            },
        )

    @callback
    def _get_schema(self):
        """Generate the schema for the user step."""
        if not self.discovered_devices:
            # No devices found: Only show refresh button
            return {
                "refresh": TextSelector(TextSelectorConfig(type="text", default="refresh")),
            }

        # Devices found: Show dropdown and refresh option
        options = {
            device["mac"]: f"{device['name']} ({device['mac']})" for device in self.discovered_devices
        }
        return {
            "mac_address": SelectSelector(
                SelectSelectorConfig(
                    options=[{"value": k, "label": v} for k, v in options.items()],
                    mode="dropdown",
                )
            ),
            "refresh": TextSelector(TextSelectorConfig(type="text", default="")),
        }
