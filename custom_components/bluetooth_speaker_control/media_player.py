import logging
from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
)
from homeassistant.const import STATE_IDLE, STATE_PLAYING, STATE_PAUSED, STATE_OFF

from .bluetooth import pair_device, connect_device, disconnect_device

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Bluetooth Speaker Control as a media player."""
    name = entry.data.get("name", "Bluetooth Speaker")
    speaker_mac = entry.data.get("mac_address")
    async_add_entities([BluetoothSpeakerMediaPlayer(name, speaker_mac)])

class BluetoothSpeakerMediaPlayer(MediaPlayerEntity):
    """Representation of a Bluetooth speaker as a media player."""

    def __init__(self, name, speaker_mac):
        """Initialize the Bluetooth speaker."""
        self._name = name
        self._speaker_mac = speaker_mac
        self._state = STATE_IDLE
        self._volume = 0.5  # Default volume (0-1)
        self._is_connected = False

    @property
    def name(self):
        """Return the name of the media player."""
        return self._name

    @property
    def state(self):
        """Return the current state of the media player."""
        return self._state

    @property
    def volume_level(self):
        """Return the volume level (0.0 to 1.0)."""
        return self._volume

    @property
    def supported_features(self):
        """Return supported features."""
        return (
            MediaPlayerEntityFeature.PLAY
            | MediaPlayerEntityFeature.PAUSE
            | MediaPlayerEntityFeature.STOP
            | MediaPlayerEntityFeature.VOLUME_SET
            | MediaPlayerEntityFeature.VOLUME_STEP
        )

    async def async_set_volume_level(self, volume):
        """Set the volume level (0-1 scale)."""
        self._volume = max(0, min(volume, 1))  # Ensure within range
        _LOGGER.info(f"🔊 Volume set to {self._volume * 100:.0f}%")
        self.async_write_ha_state()

    async def async_media_play(self):
        """Simulate playing media."""
        if self._is_connected:
            self._state = STATE_PLAYING
            _LOGGER.info("▶️ Playing media on Bluetooth speaker")
        else:
            _LOGGER.warning("⚠️ Cannot play: Bluetooth speaker not connected")
        self.async_write_ha_state()

    async def async_media_pause(self):
        """Simulate pausing media."""
        if self._is_connected:
            self._state = STATE_PAUSED
            _LOGGER.info("⏸️ Paused media on Bluetooth speaker")
        else:
            _LOGGER.warning("⚠️ Cannot pause: Bluetooth speaker not connected")
        self.async_write_ha_state()

    async def async_media_stop(self):
        """Simulate stopping media."""
        if self._is_connected:
            self._state = STATE_IDLE
            _LOGGER.info("⏹️ Stopped media on Bluetooth speaker")
        else:
            _LOGGER.warning("⚠️ Cannot stop: Bluetooth speaker not connected")
        self.async_write_ha_state()

    async def async_turn_on(self):
        """Attempt to connect to the Bluetooth speaker."""
        if self._speaker_mac:
            success = connect_device(self._speaker_mac)
            if success:
                self._is_connected = True
                self._state = STATE_IDLE
                _LOGGER.info(f"🔵 Connected to Bluetooth speaker {self._speaker_mac}")
            else:
                _LOGGER.error(f"❌ Failed to connect to {self._speaker_mac}")
        else:
            _LOGGER.error("❌ No MAC address provided for connection")
        self.async_write_ha_state()

    async def async_turn_off(self):
        """Attempt to disconnect the Bluetooth speaker."""
        if self._speaker_mac:
            success = disconnect_device(self._speaker_mac)
            if success:
                self._is_connected = False
                self._state = STATE_OFF
                _LOGGER.info(f"🔌 Disconnected from Bluetooth speaker {self._speaker_mac}")
            else:
                _LOGGER.error(f"❌ Failed to disconnect from {self._speaker_mac}")
        else:
            _LOGGER.error("❌ No MAC address provided for disconnection")
        self.async_write_ha_state()
