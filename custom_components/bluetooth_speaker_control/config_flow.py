from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN
from .bluetooth import discover_bluetooth_devices
import logging
import json
import voluptuous as vol

_LOGGER = logging.getLogger(__name__)


class BluetoothSpeakerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the configuration flow for Bluetooth Speaker Control."""

    VERSION = 1

    def __init__(self):
        self.discovered_devices = []
        self.selected_device = None

    async def async_step_user(self, user_input=None):
        """Handle the initial step: list available devices."""
        errors = {}

        if user_input is not None:
            selected_mac = user_input.get("device_mac")

            if not selected_mac or selected_mac == "none":
                _LOGGER.error("❌ Invalid selection: No device selected.")
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
                _LOGGER.info(f"🟢 Selected Bluetooth Device: {self.selected_device}")
                return await self.async_step_set_name()

            _LOGGER.error(f"❌ Selected MAC address {selected_mac} not found in discovered devices.")
            return self.async_show_form(
                step_id="user",
                data_schema=self._get_device_schema(),
                errors={"base": "device_not_found"},
            )

        _LOGGER.info("🔍 Starting Bluetooth device discovery...")
        try:
            devices = await discover_bluetooth_devices(self.hass)
            self.discovered_devices = devices
        except Exception as e:
            _LOGGER.error(f"🔥 Error during device discovery: {e}")
            return self.async_show_form(
                step_id="user",
                data_schema=self._get_device_schema(no_devices=True),
                errors={"base": "discovery_failed"},
            )

        if not self.discovered_devices:
            _LOGGER.warning(
                "⚠️ No devices discovered. Ensure devices are powered on, discoverable, and within range of the Bluetooth adapter."
            )
            return self.async_show_form(
                step_id="user",
                data_schema=self._get_device_schema(no_devices=True),
                errors={"base": "no_devices_found"},
            )

        _LOGGER.info(f"✅ Discovered {len(self.discovered_devices)} devices.")
        for device in self.discovered_devices:
            _LOGGER.info(f"🔵 Discovered Device: {device}")

        return self.async_show_form(
            step_id="user",
            data_schema=self._get_device_schema(),
        )


    async def async_step_set_name(self, user_input=None):
        """Handle the step where the user names the selected device."""
        if user_input is not None:
            _LOGGER.info(f"✅ Saving device with nickname: {user_input['nickname']}")
            return self.async_create_entry(
                title=user_input["nickname"],
                data=self.selected_device,
            )

        # Extract relevant device information
        try:
            device_name = self.selected_device.get("name", "Unknown")
            device_type = self.selected_device.get("type", "Unknown")
            device_mac = self.selected_device.get("mac", "Unknown")
            device_rssi = self.selected_device.get("rssi", "Unknown")
            device_uuids = self.selected_device.get("service_uuids", ["None"])
            device_icon = self.selected_device.get("icon", "🔵")
        except Exception as e:
            _LOGGER.error(f"⚠️ Error extracting device details: {e}")
            return self.async_abort(reason="device_details_error")

        # Format device details for display
        device_details = (
            f"**Device Information**\n\n"
            f"🔹 **Name:** {device_name}\n"
            f"{device_icon} **Type:** {device_type}\n"
            f"🔹 **MAC Address:** `{device_mac}`\n"
            f"🔹 **RSSI:** `{device_rssi} dBm`\n"
            f"🔹 **Service UUIDs:** `{', '.join(device_uuids)}`\n"
        )

        # Log the device details
        _LOGGER.info(f"🔵 Device Details: {json.dumps(self.selected_device, indent=4)}")

        # Default nickname
        default_nickname = f"{device_name} ({device_mac})"

        # Define input schema
        data_schema = vol.Schema(
            {
                vol.Required("nickname", default=default_nickname): str,
            }
        )

        return self.async_show_form(
            step_id="set_name",
            data_schema=data_schema,
            description_placeholders={"device_details": device_details},
        )

    @callback
    def _get_device_schema(self, no_devices=False):
        """Generate the schema for the list of devices."""
        if no_devices:
            return vol.Schema(
                {
                    vol.Optional("device_mac"): vol.In(
                        {"none": "No devices found. Make sure devices are discoverable and try again."}
                    )
                }
            )

        device_options = {
            device["mac"]: f"{device['icon']} {device['type']} | {device['name']} ({device['mac']}) {device['rssi']} dBm"
            for device in self.discovered_devices
        }

        return vol.Schema(
            {
                vol.Required("device_mac"): vol.In(device_options),
            }
        )

