import logging
from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
)
from homeassistant.const import STATE_IDLE, STATE_PLAYING, STATE_OFF
from .const import DOMAIN, STATE_CONNECTED, STATE_DISCONNECTED, STATE_PAIRING, STATE_FAILED
from .bluetooth import pair_device, connect_device, disconnect_device

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Bluetooth Speaker entity from a config entry."""
    mac_address = entry.data.get("mac_address")
    speaker_name = entry.data.get("name", "Bluetooth Speaker")
    async_add_entities([BluetoothSpeaker(speaker_name, mac_address)])


class BluetoothSpeaker(MediaPlayerEntity):
    """Representation of a Bluetooth speaker."""

    def __init__(self, name, speaker_mac):
        """Initialize the Bluetooth speaker."""
        self._name = name
        self._speaker_mac = speaker_mac
        self._state = STATE_DISCONNECTED
        self._volume_level = 0.5  # Default volume level
        self._is_muted = False

    @property
    def name(self):
        """Return the name of the speaker."""
        return self._name

    @property
    def state(self):
        """Return the current state of the speaker."""
        return self._state

    @property
    def supported_features(self):
        """Return the features supported by this media player."""
        return (
            MediaPlayerEntityFeature.VOLUME_SET
            | MediaPlayerEntityFeature.VOLUME_MUTE
            | MediaPlayerEntityFeature.PLAY
            | MediaPlayerEntityFeature.PAUSE
            | MediaPlayerEntityFeature.STOP
            | MediaPlayerEntityFeature.TURN_ON
            | MediaPlayerEntityFeature.TURN_OFF
        )

    async def async_turn_on(self):
        """Connect to the speaker."""
        _LOGGER.info(f"🔄 Attempting to connect to {self._name} ({self._speaker_mac})")
        if connect_device(self._speaker_mac):
            self._state = STATE_CONNECTED
            _LOGGER.info(f"✅ Connected to {self._name}")
        else:
            self._state = STATE_FAILED
            _LOGGER.error(f"❌ Failed to connect to {self._name}")
        self.async_write_ha_state()

    async def async_turn_off(self):
        """Disconnect from the speaker."""
        _LOGGER.info(f"🔄 Disconnecting from {self._name} ({self._speaker_mac})")
        if disconnect_device(self._speaker_mac):
            self._state = STATE_DISCONNECTED
            _LOGGER.info(f"✅ Disconnected from {self._name}")
        else:
            _LOGGER.error(f"❌ Failed to disconnect from {self._name}")
        self.async_write_ha_state()

    async def async_media_play(self):
        """Simulate playing media."""
        if self._state == STATE_CONNECTED:
            self._state = STATE_PLAYING
            _LOGGER.info(f"▶️ Playing on {self._name}")
            self.async_write_ha_state()

    async def async_media_pause(self):
        """Simulate pausing media."""
        if self._state == STATE_PLAYING:
            self._state = STATE_IDLE
            _LOGGER.info(f"⏸️ Paused on {self._name}")
            self.async_write_ha_state()

    async def async_media_stop(self):
        """Simulate stopping media."""
        if self._state in [STATE_PLAYING, STATE_IDLE]:
            self._state = STATE_CONNECTED
            _LOGGER.info(f"⏹️ Stopped playing on {self._name}")
            self.async_write_ha_state()

    async def async_set_volume_level(self, volume):
        """Set volume level."""
        self._volume_level = volume
        _LOGGER.info(f"🔊 Volume set to {int(volume * 100)}% on {self._name}")
        self.async_write_ha_state()

    async def async_mute_volume(self, mute):
        """Mute/unmute volume."""
        self._is_muted = mute
        _LOGGER.info(f"🔇 Muted: {mute} on {self._name}")
        self.async_write_ha_state()

    async def async_reconnect(self):
        """Reconnect to the last known speaker."""
        _LOGGER.info(f"🔄 Attempting to reconnect to {self._name} ({self._speaker_mac})")
        if connect_device(self._speaker_mac):
            self._state = STATE_CONNECTED
            _LOGGER.info(f"✅ Reconnected to {self._name}")
        else:
            self._state = STATE_FAILED
            _LOGGER.error(f"❌ Reconnection failed for {self._name}")
        self.async_write_ha_state()

    async def async_reset_bluetooth(self):
        """Reset the Bluetooth adapter."""
        _LOGGER.info("🔄 Resetting Bluetooth adapter...")
        success = disconnect_device(self._speaker_mac) and connect_device(self._speaker_mac)
        if success:
            self._state = STATE_CONNECTED
            _LOGGER.info("✅ Bluetooth adapter reset successfully")
        else:
            self._state = STATE_FAILED
            _LOGGER.error("❌ Failed to reset Bluetooth adapter")
        self.async_write_ha_state()
