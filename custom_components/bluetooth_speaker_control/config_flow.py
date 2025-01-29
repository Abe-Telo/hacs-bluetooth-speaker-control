import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.entity_component import async_update_entity
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry
from .const import DOMAIN, CONF_MAC_ADDRESS, CONF_NAME
from .bluetooth import discover_bluetooth_devices
from .media_player import BluetoothSpeaker

_LOGGER = logging.getLogger(__name__)

class BluetoothSpeakerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the configuration flow for Bluetooth Speaker Control."""

    VERSION = 1

    def __init__(self):
        self.discovered_devices = []
        self.selected_device = None
        self.passive_scanning = None

    async def async_step_user(self, user_input=None):
        """Handle the first step of the configuration flow."""
        errors = {}

        _LOGGER.info("🔍 Starting Bluetooth device discovery (config_flow).")

        try:
            self.discovered_devices = await discover_bluetooth_devices(self.hass)

            # Detect if Passive Scanning is ON or OFF based on discovered data
            if any(device.get("rssi") != -100 for device in self.discovered_devices):
                self.passive_scanning = True
                _LOGGER.info("🟢 Passive Scanning is ON. Using advertisement data.")
            else:
                self.passive_scanning = False
                _LOGGER.warning("⚠️ Passive Scanning is OFF. Using fallback scanning.")

            _LOGGER.info(f"✅ Discovered devices: {self.discovered_devices}")
        except Exception as e:
            _LOGGER.error(f"🔥 Error during device discovery: {e}")
            errors["base"] = "discovery_failed"

        # Ensure we do not proceed if no devices are found
        if not self.discovered_devices:
            _LOGGER.warning("⚠️ No Bluetooth devices discovered. Ensure devices are powered on and in range.")
            errors["base"] = "no_devices_found"
            return self.async_show_form(
                step_id="user",
                data_schema=self._get_device_schema(no_devices=True),
                errors=errors,
            )

        if user_input:
            selected_mac = user_input.get(CONF_MAC_ADDRESS)

            if not selected_mac or selected_mac == "none":
                _LOGGER.error("❌ Invalid selection: No device selected.")
                errors["base"] = "invalid_selection"
            else:
                # Find selected device
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

        _LOGGER.info(f"✅ Discovered {len(self.discovered_devices)} devices.")

        return self.async_show_form(
            step_id="user",
            data_schema=self._get_device_schema(),
            errors=errors,
        )

    async def async_step_set_name(self, user_input=None):
        """Handle the step where the user names the selected device."""
        if user_input:
            _LOGGER.info(f"✅ Saving device with nickname: {user_input[CONF_NAME]}")

            # Create a new entity for the media player
            await self._create_media_player_entity(self.selected_device, user_input[CONF_NAME])

            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data=self.selected_device,
            )

        # Extract device details
        try:
            device_name = self.selected_device.get("name", "Unknown")
            device_mac = self.selected_device.get("mac", "Unknown")
            device_rssi = self.selected_device.get("rssi", "Unknown")
            device_type = self.selected_device.get("type", "Unknown")
            device_icon = self.selected_device.get("icon", "🔵")
            device_uuids = self.selected_device.get("service_uuids", ["None"])
        except Exception as e:
            _LOGGER.error(f"⚠️ Error extracting device details: {e}")
            return self.async_abort(reason="device_details_error")

        device_details = (
            f"**Device Information**\n\n"
            f"🔹 **Name:** {device_name}\n"
            f"{device_icon} **Type:** {device_type}\n"
            f"🔹 **MAC Address:** `{device_mac}`\n"
            f"🔹 **RSSI:** `{device_rssi} dBm`\n"
            f"🔹 **Service UUIDs:** `{', '.join(device_uuids)}`\n"
        )

        _LOGGER.info(f"🔵 Device Details: {device_details}")

        default_nickname = f"{device_name} ({device_mac})"

        data_schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=default_nickname): str,
            }
        )

        return self.async_show_form(
            step_id="set_name",
            data_schema=data_schema,
            description_placeholders={"device_details": device_details},
        )

    async def _create_media_player_entity(self, device, name):
        """Create a media player entity for the discovered Bluetooth speaker."""
        _LOGGER.info(f"🎵 Adding {name} as a media player entity.")

        entity_registry = async_get_entity_registry(self.hass)
        entity_id = f"media_player.{name.lower().replace(' ', '_')}"

        if entity_id not in entity_registry.entities:
            speaker_entity = BluetoothSpeaker(name, device["mac"])
            self.hass.add_job(self.hass.states.async_set(entity_id, speaker_entity))
            await async_update_entity(self.hass, entity_id)
            _LOGGER.info(f"✅ Media player entity {entity_id} created.")
        else:
            _LOGGER.warning(f"⚠️ Media player entity {entity_id} already exists.")

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
            device["mac"]: f"{device['icon']} {device['type']} | {device['name']} ({device['mac']}) {device['rssi']} dBm"
            for device in self.discovered_devices
        }

        return vol.Schema(
            {
                vol.Required(CONF_MAC_ADDRESS): vol.In(device_options),
            }
        )
