"""Constants for the Bluetooth Speaker Control integration."""

DOMAIN = "bluetooth_speaker_control"
DEFAULT_NAME = "Bluetooth Speaker Control"

# Configuration Keys
CONF_MAC_ADDRESS = "mac_address"
CONF_NAME = "name"

# Home Assistant Events
EVENT_BLUETOOTH_DEVICE_DISCOVERED = "bluetooth_device_discovered"
EVENT_BLUETOOTH_DEVICE_CONNECTED = "bluetooth_device_connected"
EVENT_BLUETOOTH_DEVICE_DISCONNECTED = "bluetooth_device_disconnected"
EVENT_BLUETOOTH_SCAN_STARTED = "bluetooth_scan_started"
EVENT_BLUETOOTH_SCAN_COMPLETED = "bluetooth_scan_completed"

# Device States
STATE_CONNECTED = "connected"
STATE_DISCONNECTED = "disconnected"
STATE_PAIRING = "pairing"
STATE_FAILED = "failed"
STATE_SCANNING = "scanning"

# Logging & Debugging
DEBUG_MODE = True
LOG_LEVEL = "info"  # Options: "debug", "info", "warning", "error"

# Default Values
DEFAULT_SPEAKER_NAME = "Bluetooth Speaker"
DEFAULT_SCAN_INTERVAL = 15  # Seconds before automatic scan retries
DEFAULT_RECONNECT_INTERVAL = 15  # Seconds before attempting to reconnect
DEFAULT_MAX_SCAN_ATTEMPTS = 5  # Number of times to retry scanning before failing
DEFAULT_CONNECTION_TIMEOUT = 30  # Timeout for connections (in seconds)

# Services
SERVICE_PAIR_SPEAKER = "pair_speaker"
SERVICE_CONNECT_SPEAKER = "connect_speaker"
SERVICE_DISCONNECT_SPEAKER = "disconnect_speaker"
SERVICE_SCAN_DEVICES = "scan_devices"
SERVICE_RECONNECT_SPEAKER = "reconnect_speaker"
SERVICE_RESET_BLUETOOTH = "reset_bluetooth"
