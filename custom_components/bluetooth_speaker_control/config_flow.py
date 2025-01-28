from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN
from .bluetooth import discover_bluetooth_devices
import logging
import voluptuous as vol

_LOGGER = logging.getLogger(__name__)


class BluetoothSpeakerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the configuration flow for Bluetooth Speaker Control."""

    VERSION = 1

    def __init__(self):
        self.discovered_devices = []
        self.selected_device = None

    # LIST BluTooth Devices (Disovery)
    async def async_step_user(self, user_input=None):
        """Handle the initial step: list available devices."""
        if user_input is not None:
            selected_mac = user_input.get("device_mac")
            if not selected_mac or selected_mac == "none":
                _LOGGER.error("Invalid selection: No device selected.")
                return self.async_show_form(
                    step_id="user",
                    data_schema=self._get_device_schema(no_devices=not self.discovered_devices),
                    errors={"base": "invalid_selection"},
                )

            self.selected_device = next(
                (device for device in self.discovered_devices if device["mac"] == selected_mac),
                None,
            )
            if self.selected_device:
                return await self.async_step_set_name()

            _LOGGER.error(f"Selected MAC address {selected_mac} not found in discovered devices.")
            return self.async_show_form(
                step_id="user",
                data_schema=self._get_device_schema(),
                errors={"base": "device_not_found"},
            )

        self.discovered_devices = await discover_bluetooth_devices(self.hass)

        if not self.discovered_devices:
            _LOGGER.warning("No Bluetooth devices discovered.")
            return self.async_show_form(
                step_id="user",
                data_schema=self._get_device_schema(no_devices=True),
                errors={"base": "no_devices_found"},
            )

        return self.async_show_form(
            step_id="user",
            data_schema=self._get_device_schema(),
        )
    # After Selecting a Device: Name The Device
    async def async_step_set_name(self, user_input=None):
        """Handle the step where the user names the selected device."""
        if user_input is not None:
            # Create the configuration entry with all details
            return self.async_create_entry(
                title=user_input["nickname"],
                data={
                    "nickname": user_input["nickname"],
                    "name": self.selected_device["name"],
                    "type": self.selected_device["type"],
                    "mac_address": self.selected_device["mac"],
                    "manufacturer": self.selected_device["manufacturer"],
                    "rssi": self.selected_device["rssi"],
                    "uuids": self.selected_device["uuids"],
                },
            )

        # Format device details to display them nicely
        device_details = (
            f"**Device Information**\n"
            f"- **Name**: {self.selected_device['name']}\n"
            f"- **Type**: {self.selected_device['type']}\n"
            f"- **MAC Address**: {self.selected_device['mac']}\n"
            f"- **Manufacturer**: {self.selected_device['manufacturer']}\n"
            f"- **RSSI**: {self.selected_device['rssi']} dBm\n"
            f"- **Service UUIDs**: {', '.join(self.selected_device['uuids']) if self.selected_device['uuids'] else 'None'}\n"
        )

        # Set the default nickname to "Device_Name (MAC)"
        default_nickname = f"{self.selected_device['name']} ({self.selected_device['mac']} ({self.selected_device['manufacturer']} ({self.selected_device['rssi']} ({self.selected_device['uuids']} )"

        # Form schema for the nickname input
        data_schema = vol.Schema(
            {
                vol.Required("nickname", default=default_nickname): str,
            }
        )

        return self.async_show_form(
            step_id="set_name",
            data_schema=data_schema,
            description_placeholders={
                "device_details": device_details,  # Display all device information
            },
        )


    @callback
    def _get_device_schema(self, no_devices=False):
        """Generate the schema for the list of devices."""
        if no_devices:
            return vol.Schema({vol.Optional("device_mac"): vol.In({"none": "No devices found"})})

        device_options = {
            device["mac"]: f"{device['icon']} {device['type']} | {device['name']} ({device['mac']})"
            for device in self.discovered_devices
        }

        return vol.Schema(
            {
                vol.Required("device_mac"): vol.In(device_options),
            }
        )
