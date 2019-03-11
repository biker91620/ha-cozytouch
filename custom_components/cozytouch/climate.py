import logging
import voluptuous as vol

from homeassistant.const import CONF_USERNAME, CONF_PASSWORD, CONF_PLATFORM, CONF_TIMEOUT
from homeassistant.helpers import config_validation as cv
from homeassistant.components import climate
from homeassistant.const import TEMP_CELSIUS

from custom_components.cozytouch import COZYTOUCH_CLIENT_REQUIREMENT

_LOGGER = logging.getLogger(__name__)

# Requires cozytouch client library.
REQUIREMENTS = [COZYTOUCH_CLIENT_REQUIREMENT]

DEFAULT_TIMEOUT = 10
DEFAULT_TIME_OFFSET = 7200
KW_UNIT = 'kW'

CONF_COZYTOUCH_ACTUATOR = "actuator"

PLATFORM_SCHEMA = vol.Schema({
    vol.Required(CONF_PLATFORM): cv.string,
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Optional(CONF_COZYTOUCH_ACTUATOR, default="all"): cv.string,
    vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): cv.positive_int
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the sensor platform."""

    from cozypy.client import CozytouchClient
    from cozypy.constant import DeviceType

    # Assign configuration variables. The configuration check takes care they are
    # present.
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)
    timeout = config.get(CONF_TIMEOUT)
    actuator = config.get(CONF_COZYTOUCH_ACTUATOR)

    # Setup cozytouch client
    client = CozytouchClient(username, password, timeout)
    setup = client.get_setup()
    devices = []
    for heater in setup.heaters:
        if actuator == "all":
            devices.append(StandaloneCozytouchThermostat(heater))
        elif actuator == "pass" and heater.widget == DeviceType.HEATER_PASV:
            devices.append(StandaloneCozytouchThermostat(heater))
        elif actuator == "i2g" and heater.widget == DeviceType.HEATER:
            devices.append(StandaloneCozytouchThermostat(heater))


    _LOGGER.info("Found %d thermostat" % len(devices))

    add_devices(devices)


class StandaloneCozytouchThermostat(climate.ClimateDevice):
    """Representation a Netatmo thermostat."""

    def __init__(self, heater):
        """Initialize the sensor."""
        self.heater = heater
        self._state = None
        self._target_temperature = None
        self._away = None
        self._current_operation = "auto"
        self.__load_features()

    def __load_features(self):
        """Return the list of supported features."""
        self._support_flags = None

        from cozypy.constant import DeviceState
        states_mapping = [
            (DeviceState.OPERATING_MODE_STATE, climate.SUPPORT_OPERATION_MODE),
            (DeviceState.COMFORT_TEMPERATURE_STATE, climate.SUPPORT_TARGET_TEMPERATURE_HIGH),
            (DeviceState.ECO_TEMPERATURE_STATE, climate.SUPPORT_TARGET_TEMPERATURE_LOW),
            (DeviceState.AWAY_STATE, climate.SUPPORT_AWAY_MODE)
        ]
        for state, flag in states_mapping:
            if self.heater.is_state_supported(state):
                self._support_flags = self._support_flags | flag if self._support_flags is not None else flag

    @property
    def operation_list(self):
        return self.heater.operation_list

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return self._support_flags

    @property
    def name(self):
        """Return the name of the sensor."""
        return "%s %s" % (self.heater.place.name, self.heater.name)

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self.heater.temperature

    @property
    def target_temperature_high(self):
        return self.heater.comfort_temperature

    @property
    def target_temperature_low(self):
        return self.heater.eco_temperature

    @property
    def current_operation(self):
        """Return the current state of the thermostat."""
        return self.heater.operation_mode

    @property
    def is_away_mode_on(self):
        """Return true if away mode is on."""
        return self.heater.is_away

    def set_operation_mode(self, operation_mode):
        """Change operation mode."""
        self.heater.set_operation_mode(operation_mode)

    def turn_away_mode_on(self):
        """Turn away on."""
        self.heater.turn_away_mode_on()

    def turn_away_mode_off(self):
        """Turn away off."""
        self.heater.turn_away_mode_off()

    def set_temperature(self, **kwargs):
        """Set new target temperature"""
        if "target_temp_low" in kwargs:
            self.heater.set_eco_temperature(kwargs["target_temp_low"])
        if "target_temp_high" in kwargs:
            self.heater.set_eco_temperature(kwargs["target_temp_high"])

    def update(self):
        """Fetch new state data for this sensor."""
        _LOGGER.info("Update thermostat %s" % self.name)
        self.heater.update()

