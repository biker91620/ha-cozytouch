import logging
import voluptuous as vol
from homeassistant.components.climate import const

from homeassistant.const import CONF_USERNAME, CONF_PASSWORD, CONF_PLATFORM, CONF_TIMEOUT, CONF_SCAN_INTERVAL
from homeassistant.components.climate import PLATFORM_SCHEMA
from homeassistant.helpers import config_validation as cv
from homeassistant.components import climate
from homeassistant.const import TEMP_CELSIUS

from custom_components.cozytouch import COZYTOUCH_CLIENT_REQUIREMENT

_LOGGER = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 10
DEFAULT_TIME_OFFSET = 7200
KW_UNIT = 'kW'

DEFAULT_SCAN_INTERVAL = 60

CONF_COZYTOUCH_ACTUATOR = "actuator"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_PLATFORM): cv.string,
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Optional(CONF_COZYTOUCH_ACTUATOR, default="all"): cv.string,
    vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): cv.positive_int,
    vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.time_period_seconds
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

    # Setup cozytouch client
    client = CozytouchClient(username, password, timeout)
    setup = client.get_setup()
    devices = []
    for heater in setup.heaters:
        if heater.widget == DeviceType.HEATER:
            devices.append(StandaloneCozytouchThermostat(heater))


    _LOGGER.info("Found {count} thermostat".format(count=len(devices)))

    add_devices(devices)


class StandaloneCozytouchThermostat(climate.ClimateDevice):
    """Representation a Netatmo thermostat."""

    def __init__(self, heater):
        """Initialize the sensor."""
        self.heater = heater
        self._support_flags = None
        self._state = None
        self._target_temperature = None
        self._away = None
        self._preset_modes = [const.PRESET_SLEEP, const.PRESET_ECO, const.PRESET_COMFORT]
        self._hvac_modes=[const.HVAC_MODE_HEAT, const.HVAC_MODE_OFF, const.HVAC_MODE_AUTO]
        self.__load_features()

    def __set_support_flags(self, flag):
        self._support_flags = self._support_flags | flag if self._support_flags is not None else flag

    def __load_features(self):
        """Return the list of supported features."""
        from cozypy.constant import DeviceState

        if self.heater.is_state_supported(DeviceState.TARGETING_HEATING_LEVEL_STATE):
            self.__set_support_flags(const.SUPPORT_PRESET_MODE)
        if self.heater.is_state_supported(DeviceState.ECO_TEMPERATURE_STATE) and self.heater.is_state_supported(DeviceState.COMFORT_TEMPERATURE_STATE):
            self.__set_support_flags(const.SUPPORT_TARGET_TEMPERATURE_RANGE)
        else:
            self.__set_support_flags(const.SUPPORT_TARGET_TEMPERATURE)


    @property
    def supported_features(self):
        """Return the list of supported features."""
        return self._support_flags

    @property
    def name(self):
        """Return the name of the sensor."""
        return "{place} {heater}".format(place=self.heater.place.name, heater=self.heater.name)

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
    def hvac_mode(self):
        """Return hvac target hvac state."""
        from cozypy.constant import OperatingModeState

        if self.heater.operating_mode == OperatingModeState.STANDBY:
            return const.HVAC_MODE_OFF
        elif self.heater.operating_mode == OperatingModeState.BASIC:
            return const.HVAC_MODE_HEAT
        elif self.heater.operating_mode == OperatingModeState.INTERNAL:
            return const.HVAC_MODE_AUTO
        elif self.heater.operating_mode == OperatingModeState.AUTO:
            return const.HVAC_MODE_AUTO
        return const.HVAC_MODE_OFF

    @property
    def hvac_modes(self):
        """Return the list of available operating modes."""
        return self._hvac_modes

    @property
    def is_away_mode_on(self):
        """Return true if away mode is on."""
        return self.heater.is_away

    @property
    def preset_mode(self):
        """Return the current preset mode."""
        from cozypy.constant import TargetingHeatingLevelState
        if self.heater.target_heating_level == TargetingHeatingLevelState.ECO:
            return const.PRESET_ECO
        if self.heater.target_heating_level == TargetingHeatingLevelState.COMFORT:
            return const.PRESET_COMFORT
        return const.PRESET_SLEEP

    @property
    def preset_modes(self):
        """Return a list of available preset modes."""
        return self._preset_modes

    def turn_away_mode_on(self):
        """Turn away on."""
        self.heater.turn_away_mode_on()

    def turn_away_mode_off(self):
        """Turn away off."""
        self.heater.turn_away_mode_off()

    def set_temperature(self, **kwargs):
        """Set new target temperature"""
        if const.ATTR_TARGET_TEMP_HIGH in kwargs:
            self.heater.set_comfort_temperature(kwargs[const.ATTR_TARGET_TEMP_HIGH])
            _LOGGER.info("Set HIGH TEMP to {temp}".format(temp=kwargs[const.ATTR_TARGET_TEMP_HIGH]))
        if const.ATTR_TARGET_TEMP_LOW in kwargs:
            self.heater.set_eco_temperature(kwargs[const.ATTR_TARGET_TEMP_LOW])
            _LOGGER.info("Set LOW TEMP to {temp}".format(temp=kwargs[const.ATTR_TARGET_TEMP_LOW]))

    def set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode. HVAC_MODE_AUTO, HVAC_MODE_HEAT, HVAC_MODE_OFF"""
        from cozypy.constant import OperatingModeState

        if hvac_mode == const.HVAC_MODE_OFF:
            self.heater.set_operating_mode(OperatingModeState.STANDBY)
        elif hvac_mode == const.HVAC_MODE_HEAT:
            self.heater.set_operating_mode(OperatingModeState.BASIC)
        elif hvac_mode == const.HVAC_MODE_AUTO:
            self.heater.set_operating_mode(OperatingModeState.INTERNAL)

    def set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode. PRESET_ECO, PRESET_COMFORT"""
        from cozypy.constant import TargetingHeatingLevelState

        if preset_mode == const.PRESET_SLEEP:
            self.heater.set_targeting_heating_level(TargetingHeatingLevelState.FROST_PROTECTION)
        elif preset_mode == const.PRESET_ECO:
            self.heater.set_targeting_heating_level(TargetingHeatingLevelState.ECO)
        elif preset_mode == const.PRESET_COMFORT:
            self.heater.set_targeting_heating_level(TargetingHeatingLevelState.COMFORT)

    def update(self):
        """Fetch new state data for this sensor."""
        _LOGGER.info("Update thermostat {name}".format(name=self.name))
        self.heater.update()
