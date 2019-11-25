"""Constants for the Cozytouch component."""
import logging

LOGGER = logging.getLogger(__package__)

DOMAIN = "cozytouch"
COMPONENTS = ["sensor", "binary_sensor", "climate", "switch"]
DEFAULT_TIMEOUT = 10
DEFAULT_SCAN_INTERVAL = 60

DEFAULT_TIMEOUT = 10
DEFAULT_TIME_OFFSET = 7200
KW_UNIT = 'kW'

CONF_COZYTOUCH_ACTUATOR = "actuator"

