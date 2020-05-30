"""Constants for the Cozytouch component."""
import logging

LOGGER = logging.getLogger(__package__)

DOMAIN = "cozytouch"
COZYTOUCH_DATAS = "cozy_datas"
COMPONENTS = ["climate", "switch", "water_heater", "binary_sensor", "sensor"]
SENSOR_TYPES = ["all", "pass", "i2g"]

DEFAULT_TIMEOUT = 10
DEFAULT_SCAN_INTERVAL = 60
DEFAULT_TIMEOUT = 10
DEFAULT_TIME_OFFSET = 7200
KW_UNIT = "kW"
COZYTOUCH_ACTUATOR = "model"
CONF_COZYTOUCH_ACTUATOR = "model"
DEFAULT_COZYTOUCH_ACTUATOR = "all"

STATE_AUTO = "auto"
STATE_MANUEL = "manuel"
STATE_COMFORT = "comfort"
STATE_STOP = "stop"
STATE_EXTERNAL = "external"
SERVICE_SET_AWAY_MODE = "set_away_mode"
SERVICE_SET_BOOST_MODE = "set_boost_mode"
SERVICE_SET_OPERATION_MODE = "set_operation_mode"

ATTR_TIME_PERIOD = "time_period"
ATTR_OPERATION_MODE = "boiler_opmode"
