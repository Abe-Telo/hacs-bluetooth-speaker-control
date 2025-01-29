import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, CONF_MAC_ADDRESS, CONF_NAME
from .bluetooth import discover_bluetooth_devices
from homeassistant.helpers.entity_component import async_update_entity
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry

_LOGGER = logging.getLogger(__name__)

class BluetoothSpeakerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the configuration flow for Bluetooth Speaker Control."""

    VERSION = 1

    def __init__(self):
        self.discovered_devices = []
        self.selected_device = None

    async def async_step_user(self, user_input=None):
        """Handle the first step of the configuration flow."""
        errors = {}

        _LOGGER.info("🔍 Starting Bluetooth device discovery (config_flow).")
        try: 
            passive_mode = self.hass.data.get("bluetooth_speaker_control_passive", False)
            self.discovered_devices = await discover_bluetooth_devices(self.hass, timeout=7, passive_scanning=passive_mode)

            _LOGGER.info(f"✅ Discovered devices: {self.discovered_devices}")
        except Exception as e:
            _LOGGER.error(f"🔥 Error during device discovery: {e}")
            errors["base"] = "discovery_failed"

        if user_input:
            selected_mac = user_input.get(CONF_MAC_ADDRESS)

            if not selected_mac or selected_mac == "none":
                _LOGGER.error("❌ Invalid selection: No device selected.")
                errors["base"] = "invalid_selection"
            else:
                self.selected_device = next(
                    (device for device in self.discovered_devices if device["mac"] == selected_mac),
                    None,
                )
                if self.selected_device:
                    _LOGGER.info(f"🟢 Selected Bluetooth Device: {self.selected_device}")
                    return await self.async_step_set_name()
                else:
                    _LOGGER.error(f"❌ Selected MAC address {selected_mac} not found in discovered devices.")
                    errors["base"] = "device_not_found"

        if not self.discovered_devices:
            _LOGGER.warning("⚠️ No Bluetooth devices discovered. Ensure devices are powered on and in range.")
            errors["base"] = "no_devices_found"

        return self.async_show_form(
            step_id="user",
            data_schema=self._get_device_schema(no_devices=not self.discovered_devices),
            errors=errors,
        )

    async def async_step_set_name(self, user_input=None):
        """Handle the step where the user names the selected device."""
        if user_input:
            _LOGGER.info(f"✅ Saving device with nickname: {user_input[CONF_NAME]}")

            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data=self.selected_device,
            )

        try:
            device_details = (
                f"**Device Information**\n\n"
                f"🔹 **Name:** {self.selected_device.get('name', 'Unknown')}\n"
                f"🔹 **MAC Address:** `{self.selected_device.get('mac', 'Unknown')}`\n"
                f"🔹 **RSSI:** `{self.selected_device.get('rssi', 'Unknown')} dBm`\n"
                f"🔹 **Service UUIDs:** `{', '.join(self.selected_device.get('service_uuids', ['None']))}`\n"
            )
        except Exception as e:
            _LOGGER.error(f"⚠️ Error extracting device details: {e}")
            return self.async_abort(reason="device_details_error")

        return self.async_show_form(
            step_id="set_name",
            data_schema=vol.Schema(
                {vol.Required(CONF_NAME, default=self.selected_device["name"]): str}
            ),
            description_placeholders={"device_details": device_details},
        )

    @callback
    def _get_device_schema(self, no_devices=False):
        """Generate the schema for the list of devices."""
        if no_devices:
            return vol.Schema(
                {
                    vol.Optional(CONF_MAC_ADDRESS): vol.In(
                        {"none": "No devices found. Ensure devices are discoverable and try again."}
                    )
                }
            )

        device_options = {
            device["mac"]: f"{device['name']} ({device['mac']}) {device['rssi']} dBm"
            for device in self.discovered_devices
        }

        return vol.Schema({vol.Required(CONF_MAC_ADDRESS): vol.In(device_options)})
