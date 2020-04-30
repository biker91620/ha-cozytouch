"""Constants for the Cozytouch component."""
import logging

LOGGER = logging.getLogger(__package__)

DOMAIN = "cozytouch"
COZYTOUCH_DATAS = "cozy_datas"
COMPONENTS = ["climate", "switch", "water_heater", "binary_sensor", "sensor"]
DEFAULT_TIMEOUT = 10
DEFAULT_SCAN_INTERVAL = 60
DEFAULT_TIMEOUT = 10
DEFAULT_TIME_OFFSET = 7200
KW_UNIT = "kW"
CONF_COZYTOUCH_ACTUATOR = "actuator"

STATE_AUTO = "auto"
STATE_MANUEL = "manuel"
SERVICE_SET_AWAY_MODE = "set_away_mode"
SERVICE_SET_BOOST_MODE = "set_boost_mode"
ATTR_TIME_PERIOD = "time_period"
