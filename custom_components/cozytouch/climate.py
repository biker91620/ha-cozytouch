"""Climate sensors for Cozytouch."""
import logging

from cozytouchpy import CozytouchException
from cozytouchpy.constant import (
    DeviceState,
    DeviceType,
    ModeState,
    TargetingHeatingLevelState,
)

from homeassistant.components.climate import ClimateEntity, const
from homeassistant.const import TEMP_CELSIUS

from .const import COZYTOUCH_DATAS, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set the sensor platform."""
    datas = hass.data[DOMAIN][config_entry.entry_id][COZYTOUCH_DATAS]

    devices = []
    for heater in datas.heaters:
        if heater.widget == DeviceType.HEATER:
            devices.append(CozytouchStandaloneThermostat(heater))

    _LOGGER.info("Found {count} thermostat".format(count=len(devices)))
    async_add_entities(devices, True)


class CozytouchStandaloneThermostat(ClimateEntity):
    """Representation a thermostat."""

    def __init__(self, heater):
        """Initialize the sensor."""
        self.heater = heater
        self._support_flags = None
        self._state = None
        self._target_temperature = None
        self._away = None
        self._preset_modes = [
            const.PRESET_SLEEP,
            const.PRESET_ECO,
            const.PRESET_COMFORT,
        ]
        self._hvac_modes = [
            const.HVAC_MODE_HEAT,
            const.HVAC_MODE_OFF,
            const.HVAC_MODE_AUTO,
        ]
        self.__load_features()

    def __set_support_flags(self, flag):
        self._support_flags = (
            self._support_flags | flag if self._support_flags is not None else flag
        )

    def __load_features(self):
        """Return the list of supported features."""
        if self.heater.is_state_supported(DeviceState.TARGETING_HEATING_LEVEL_STATE):
            self.__set_support_flags(const.SUPPORT_PRESET_MODE)
        if self.heater.is_state_supported(
            DeviceState.ECO_TEMPERATURE_STATE
        ) and self.heater.is_state_supported(DeviceState.COMFORT_TEMPERATURE_STATE):
            self.__set_support_flags(const.SUPPORT_TARGET_TEMPERATURE_RANGE)
        else:
            self.__set_support_flags(const.SUPPORT_TARGET_TEMPERATURE)

    @property
    def unique_id(self):
        """Return the unique id of this sensor."""
        return self.heater.id

    @property
    def name(self):
        """Return the name of the sensor."""
        return "{place} {heater}".format(
            place=self.heater.place.name, heater=self.heater.name
        )

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return self._support_flags

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self.heater.temperature

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "name": self.name,
            "identifiers": {(DOMAIN, self.unique_id)},
            "manufacturer": "Cozytouch",
            "via_device": (DOMAIN, self.heater.data["placeOID"]),
        }

    @property
    def target_temperature_high(self):
        """Return the high temperature."""
        return self.heater.comfort_temperature

    @property
    def target_temperature_low(self):
        """Return the low temperature."""
        return self.heater.eco_temperature

    @property
    def hvac_mode(self):
        """Return hvac target hvac state."""
        if self.heater.operating_mode == ModeState.STANDBY:
            return const.HVAC_MODE_OFF
        elif self.heater.operating_mode == ModeState.BASIC:
            return const.HVAC_MODE_HEAT
        elif self.heater.operating_mode == ModeState.INTERNAL:
            return const.HVAC_MODE_AUTO
        elif self.heater.operating_mode == ModeState.AUTO:
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
        if self.heater.target_heating_level == TargetingHeatingLevelState.ECO:
            return const.PRESET_ECO
        if self.heater.target_heating_level == TargetingHeatingLevelState.COMFORT:
            return const.PRESET_COMFORT
        return const.PRESET_SLEEP

    @property
    def preset_modes(self):
        """Return a list of available preset modes."""
        return self._preset_modes

    async def async_turn_away_mode_on(self):
        """Turn away on."""
        await self.heater.turn_away_mode_on()

    async def async_turn_away_mode_off(self):
        """Turn away off."""
        await self.heater.turn_away_mode_off()

    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""
        if const.ATTR_TARGET_TEMP_HIGH in kwargs:
            await self.heater.set_comfort_temperature(
                kwargs[const.ATTR_TARGET_TEMP_HIGH]
            )
            _LOGGER.info(
                "Set HIGH TEMP to {temp}".format(
                    temp=kwargs[const.ATTR_TARGET_TEMP_HIGH]
                )
            )
        if const.ATTR_TARGET_TEMP_LOW in kwargs:
            await self.heater.set_eco_temperature(kwargs[const.ATTR_TARGET_TEMP_LOW])
            _LOGGER.info(
                "Set LOW TEMP to {temp}".format(temp=kwargs[const.ATTR_TARGET_TEMP_LOW])
            )

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode. HVAC_MODE_AUTO, HVAC_MODE_HEAT, HVAC_MODE_OFF."""
        if hvac_mode == const.HVAC_MODE_OFF:
            await self.heater.set_operating_mode(ModeState.STANDBY)
        elif hvac_mode == const.HVAC_MODE_HEAT:
            await self.heater.set_operating_mode(ModeState.BASIC)
        elif hvac_mode == const.HVAC_MODE_AUTO:
            await self.heater.set_operating_mode(ModeState.INTERNAL)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode. PRESET_ECO, PRESET_COMFORT."""
        if preset_mode == const.PRESET_SLEEP:
            await self.heater.set_targeting_heating_level(
                TargetingHeatingLevelState.FROST_PROTECTION
            )
        elif preset_mode == const.PRESET_ECO:
            await self.heater.set_targeting_heating_level(
                TargetingHeatingLevelState.ECO
            )
        elif preset_mode == const.PRESET_COMFORT:
            await self.heater.set_targeting_heating_level(
                TargetingHeatingLevelState.COMFORT
            )

    async def async_update(self):
        """Fetch new state data for this sensor."""
        _LOGGER.debug("Update thermostat {name}".format(name=self.name))
        try:
            await self.heater.update()
        except CozytouchException:
            _LOGGER.error("Device data no retrieve {}".format(self.name))
