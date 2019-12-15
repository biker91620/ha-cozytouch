"""Climate sensors for Cozytouch."""
import logging
import voluptuous as vol

from cozypy.client import CozytouchClient
from cozypy.constant import DeviceType

from homeassistant.const import CONF_USERNAME, CONF_PASSWORD, CONF_TIMEOUT, CONF_SCAN_INTERVAL
from homeassistant.components.water_heater import const
from homeassistant.components import water_heater
from homeassistant.const import TEMP_CELSIUS

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

MODE_LIST = [SUPPORT_OPERATION_MODE, SUPPORT_AWAY_MODE]

async def async_setup_entry(hass, config, async_add_entities):
    """Setup the sensor platform."""


    # Assign configuration variables. The configuration check takes care they are
    # present.
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)
    timeout = config.get(CONF_TIMEOUT)

    # Setup cozytouch client
    client = CozytouchClient(username, password, timeout)
    setup = client.get_setup()
    devices = []
    for water_heater in setup.water_heaters:
        if water_heater.widget == DeviceType.WATER_HEATER:
            devices.append(StandaloneCozytouchWaterHeater(water_heater))


    _LOGGER.info("Found {count} water heater".format(count=len(devices)))
    async_add_entities(devices, True)


class StandaloneCozytouchWaterHeater(water_heater.WaterHeaterDevice):
    """Representation a Netatmo thermostat."""

    def __init__(self, water_heater):
        """Initialize the sensor."""
        self.water_heater = water_heater
        self.precision = None
        self._support_flags = None
        self._state = None
        self._target_temperature = None
        self._away = None
        self.__load_features()

    @property
    def name(self):
        """Return the name of the sensor."""
        return self.water_heater.name

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def current_operation(self):
        """Return current operation ie. eco, electric, performance, ..."""
        return self.water_heater.operating_mode

    @property
    def operation_list(self):
        """Return the list of available operation modes."""
        return  MODE_LIST

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return self.water_heater.supported_states

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self.water_heater.get_state(DeviceState.TEMPERATURE_STATE)

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self.water_heater.get_state(DeviceState.TARGET_TEMPERATURE_STATE)

    @property
    def is_away_mode_on(self):
        """Return true if away mode is on."""
        return self.water_heater.is_away

    def set_temperature(self, **kwargs):
        """Set new target temperature."""
        raise None

    def set_operation_mode(self, operation_mode):
        """Set new target operation mode."""
        raise None

    def turn_away_mode_on(self):
        """Turn away on."""
        self.water_heater.turn_away_mode_on()

    def turn_away_mode_off(self):
        """Turn away off."""
        self.water_heater.turn_away_mode_off()

    def update(self):
        """Fetch new state data for this sensor."""
        _LOGGER.info("Update water heater {name}".format(name=self.name))
        self.water_heater.update()

    @property
    def device_info(self):
        """Return the device info."""

        return {
            "name": self.name,
            "identifiers": {(DOMAIN, self.unique_id)},
            "manufacturer": "Cozytouch",
            "via_device": (DOMAIN, "cozytouch"),
        }
