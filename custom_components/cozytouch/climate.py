"""Climate sensors for Cozytouch."""
import logging

from cozytouchpy.constant import DeviceState, DeviceType, ThermalState
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    ATTR_TARGET_TEMP_HIGH,
    ATTR_TARGET_TEMP_LOW,
    SUPPORT_PRESET_MODE,
    SUPPORT_TARGET_TEMPERATURE,
    SUPPORT_TARGET_TEMPERATURE_RANGE,
)

from homeassistant.const import TEMP_CELSIUS

from . import ClimateSchema
from .const import (
    COZY_TO_PRESET_MODE,
    COORDINATOR,
    DOMAIN,
    HEATER_TO_HVAC_MODE,
    HEATING_TO_HVAC_MODE,
    HEATINGCOOLING_TO_HVAC_MODE,
    HVAC_MODE_OFF,
    HVAC_MODE_TO_HEATER,
    HVAC_MODE_TO_HEATING,
    HVAC_MODE_TO_HEATINGCOOLING,
    PRESET_MODE_TO_COZY,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set the sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]
    devices = []
    for device in coordinator.data.devices.values():
        if device.widget == DeviceType.HEATER:
            devices.append(CozytouchStandaloneThermostat(device, coordinator))

        if device.widget == DeviceType.APC_HEATING_COOLING_ZONE:
            devices.append(
                CozytouchStandaloneThermostat(device, coordinator, ThermalState.HEAT)
            )
            devices.append(
                CozytouchStandaloneThermostat(device, coordinator, ThermalState.COOL)
            )
        elif device.widget == DeviceType.APC_HEATING_ZONE:
            devices.append(
                CozytouchStandaloneThermostat(device, coordinator, ThermalState.HEAT)
            )
    async_add_entities(devices)


class CozytouchStandaloneThermostat(CoordinatorEntity, ClimateEntity):
    """Representation a thermostat."""

    def __init__(self, device, coordinator, mode=None):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self.climate = device
        self._mode = mode
        self._support_flags = None
        self._state = None
        self._target_temperature = None
        self._away = None
        self.__load_features()
        self._schema = ClimateSchema(self.climate .widget)

    def __set_support_flags(self, flag):
        self._support_flags = (
            self._support_flags | flag if self._support_flags is not None else flag
        )

    def __load_features(self):
        """Return the list of supported features."""
        if (
            self.climate.is_state_supported(DeviceState.PASS_APC_HEATING_MODE_STATE)
            or self.climate.is_state_supported(DeviceState.PASS_APC_COOLING_MODE_STATE)
            or self.climate.is_state_supported(
                DeviceState.TARGETING_HEATING_LEVEL_STATE
            )
        ):
            self.__set_support_flags(SUPPORT_PRESET_MODE)

        if (
            (
                self.climate.is_state_supported(
                    DeviceState.ECO_COOLING_TARGET_TEMPERATURE_STATE
                )
                and self.climate.is_state_supported(
                    DeviceState.COMFORT_COOLING_TARGET_TEMPERATURE_STATE
                )
            )
            or (
                self.climate.is_state_supported(DeviceState.ECO_TEMPERATURE_STATE)
                and self.climate.is_state_supported(
                    DeviceState.COMFORT_TEMPERATURE_STATE
                )
            )
            or (
                self.climate.is_state_supported(
                    DeviceState.ECO_HEATING_TARGET_TEMPERATURE_STATE
                )
                and self.climate.is_state_supported(
                    DeviceState.COMFORT_HEATING_TARGET_TEMPERATURE_STATE
                )
            )
        ):
            self.__set_support_flags(SUPPORT_TARGET_TEMPERATURE_RANGE)
        else:
            self.__set_support_flags(SUPPORT_TARGET_TEMPERATURE)

    @property
    def unique_id(self):
        """Return the unique id of this sensor."""
        return f"{self.climate.id}{self._mode}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return "{climate}".format(climate=self.climate.name)

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
        return self.coordinator.data.devices[self.unique_id].temperature

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "name": self.name,
            "identifiers": {(DOMAIN, self.climate.id)},
            "manufacturer": self.climate.manufacturer,
            "via_device": (DOMAIN, self.climate.data["placeOID"]),
        }

    @property
    def target_temperature_step(self):
        """Return the high temperature."""
        return 0.5

    @property
    def target_temperature(self):
        """Return the high temperature."""
        return self.coordinator.data.devices[self.unique_id].target_temperature

    @property
    def target_temperature_high(self):
        """Return the high temperature."""
        if self._mode == ThermalState.COOL:
            return self.coordinator.data.devices[self.unique_id].target_comfort_cooling_temperature
        return self.coordinator.data.devices[self.unique_id].target_comfort_temperature

    @property
    def target_temperature_low(self):
        """Return the low temperature."""
        if self._mode == ThermalState.COOL:
            return self.coordinator.data.devices[self.unique_id].target_eco_cooling_temperature
        return self.coordinator.data.devices[self.unique_id].target_eco_temperature

    @property
    def hvac_mode(self):
        """Return hvac target hvac state."""
        if self.climate.widget == DeviceType.HEATER:
            return HEATER_TO_HVAC_MODE[self.climate.operating_mode]
        if self.climate.widget == DeviceType.APC_HEATING_ZONE:
            return HEATING_TO_HVAC_MODE[self.climate.operating_mode]
        if self.climate.widget == DeviceType.APC_HEATING_COOLING_ZONE:
            return HEATINGCOOLING_TO_HVAC_MODE[self.climate.operating_mode]

    @property
    def hvac_modes(self):
        """Return the list of available operating modes."""
        return self._schema.hvac_list()

    @property
    def is_away_mode_on(self):
        """Return true if away mode is on."""
        return self.coordinator.data.devices[self.unique_id].is_away

    @property
    def preset_mode(self):
        """Return the current preset mode."""
        preset = self.coordinator.data.devices[self.unique_id].preset_mode
        if self._mode == ThermalState.COOL:
            preset = self.coordinator.data.devices[self.unique_id].preset_cooling_mode
        return COZY_TO_PRESET_MODE[preset]

    @property
    def preset_modes(self):
        """Return a list of available preset modes."""
        return self._schema.preset_list()

    @property
    def extra_state_attributes(self):
        """Device attributes."""
        return {
            "preset": self.climate.preset_mode,
            "presets": self.climate.preset_mode_list,
            "mode": self.climate.operating_mode,
            "modes": self.climate.operating_mode_list,
        }

    async def async_turn_away_mode_on(self):
        """Turn away on."""
        await self.climate.turn_away_mode_on()
        await self.coordinator.async_request_refresh()

    async def async_turn_away_mode_off(self):
        """Turn away off."""
        await self.climate.turn_away_mode_off()
        await self.coordinator.async_request_refresh()

    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""
        if ATTR_TARGET_TEMP_HIGH in kwargs:
            if self.climate.widget == DeviceType.APC_HEATING_COOLING_ZONE:
                await self.climate.set_comfort_temperature(
                    kwargs[ATTR_TARGET_TEMP_HIGH], self._mode
                )
            else:
                await self.climate.set_comfort_temperature(
                    kwargs[ATTR_TARGET_TEMP_HIGH]
                )
            _LOGGER.info(
                "Set HIGH TEMP to %s  %s", kwargs[ATTR_TARGET_TEMP_HIGH], self._mode
            )
        if ATTR_TARGET_TEMP_LOW in kwargs:
            if self.climate.widget == DeviceType.APC_HEATING_COOLING_ZONE:
                await self.climate.set_eco_temperature(
                    kwargs[ATTR_TARGET_TEMP_LOW], self._mode
                )
            else:
                await self.climate.set_eco_temperature(kwargs[ATTR_TARGET_TEMP_LOW])
            _LOGGER.info(
                "Set LOW TEMP to %s %s", kwargs[ATTR_TARGET_TEMP_LOW], self._mode
            )
        await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode. HVAC_MODE_AUTO, HVAC_MODE_HEAT, HVAC_MODE_OFF."""
        if hvac_mode == HVAC_MODE_OFF:
            await self.climate.turn_off()
        elif self.climate.widget == DeviceType.HEATER:
            await self.climate.set_operating_mode(HVAC_MODE_TO_HEATER[hvac_mode])
        elif self.climate.widget == DeviceType.APC_HEATING_ZONE:
            await self.climate.set_operating_mode(HVAC_MODE_TO_HEATING[hvac_mode])
        elif self.climate.widget == DeviceType.APC_HEATING_COOLING_ZONE:
            await self.climate.set_operating_mode(
                HVAC_MODE_TO_HEATINGCOOLING[hvac_mode]
            )
        await self.coordinator.async_request_refresh()

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode. PRESET_ECO, PRESET_COMFORT."""
        if self.climate.widget == DeviceType.APC_HEATING_COOLING_ZONE:
            await self.climate.set_preset_mode(
                PRESET_MODE_TO_COZY[preset_mode], self._mode
            )
        else:
            await self.climate.set_preset_mode(PRESET_MODE_TO_COZY[preset_mode])
        await self.coordinator.async_request_refresh()
