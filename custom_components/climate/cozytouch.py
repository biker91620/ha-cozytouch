import logging
from datetime import timedelta

from cozypy.client import CozytouchClient
from cozypy.constant import DeviceType, DeviceState
from cozypy.exception import CozytouchException

from homeassistant.components.climate import ClimateDevice, SUPPORT_TARGET_TEMPERATURE_HIGH, \
    SUPPORT_TARGET_TEMPERATURE_LOW, SUPPORT_OPERATION_MODE, SUPPORT_ON_OFF, SUPPORT_AWAY_MODE, SUPPORT_TARGET_TEMPERATURE
from homeassistant.components.climate.demo import DemoClimate
from homeassistant.const import TEMP_CELSIUS
from homeassistant.util import Throttle

logger = logging.getLogger("cozytouch.climate")

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the sensor platform."""

    if "userId" not in config or "userPassword" not in config:
        raise CozytouchException("Bad configuration")

    actuator = config["actuator"] if "actuator" in config else "all"

    client = CozytouchClient(config.get("userId"), config.get("userPassword"))
    setup = client.get_setup()
    devices = []
    for heater in setup.heaters:
        if actuator == "all":
            devices.append(StandaloneCozytouchThermostat(heater))
        elif actuator == "pass" and heater.widget == DeviceType.HEATER_PASV:
            devices.append(StandaloneCozytouchThermostat(heater))
        elif actuator == "i2g" and heater.widget == DeviceType.HEATER:
            devices.append(StandaloneCozytouchThermostat(heater))


    logger.info("Found %d thermostat" % len(devices))

    add_devices(devices)


DEFAULT_TIME_OFFSET = 7200


class StandaloneCozytouchThermostat(ClimateDevice):
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

        states_mapping = [
            (DeviceState.ON_OFF_STATE, SUPPORT_ON_OFF),
            (DeviceState.OPERATING_MODE_STATE, SUPPORT_OPERATION_MODE),
            (DeviceState.COMFORT_TEMPERATURE_STATE, SUPPORT_TARGET_TEMPERATURE_HIGH),
            (DeviceState.ECO_TEMPERATURE_STATE, SUPPORT_TARGET_TEMPERATURE_LOW),
            (DeviceState.AWAY_STATE, SUPPORT_AWAY_MODE)
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

    @Throttle(timedelta(seconds=10))
    def update(self):
        logger.info("Update thermostat %s" % self.name)
        self.heater.update()

