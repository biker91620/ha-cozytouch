"""Climate sensors for Cozytouch."""
import logging

import voluptuous as vol
from cozytouchpy import CozytouchException
from cozytouchpy.constant import DeviceState, DeviceType

import homeassistant.helpers.config_validation as cv
from homeassistant.components.water_heater import (
    ATTR_TEMPERATURE,
    STATE_ECO,
    STATE_ON,
    STATE_OFF,
    SUPPORT_AWAY_MODE,
    SUPPORT_OPERATION_MODE,
    SUPPORT_TARGET_TEMPERATURE,
    WaterHeaterEntity,
)
from homeassistant.const import ATTR_ENTITY_ID, TEMP_CELSIUS

from .const import (
    ATTR_TIME_PERIOD,
    COZYTOUCH_DATAS,
    DOMAIN,
    SERVICE_SET_AWAY_MODE,
    SERVICE_SET_BOOST_MODE,
    STATE_AUTO,
    STATE_MANUEL,
    STATE_COMFORT,
    STATE_EXTERNAL,
)

_LOGGER = logging.getLogger(__name__)

AWAY_MODE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_id,
        vol.Required(ATTR_TIME_PERIOD): cv.positive_int,
    }
)

BOOST_MODE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_id,
        vol.Required(ATTR_TIME_PERIOD): vol.All(
            cv.positive_int, vol.Range(min=0, max=7)
        ),
    }
)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set the sensor platform."""
    datas = hass.data[DOMAIN][config_entry.entry_id][COZYTOUCH_DATAS]

    devices = []
    for water_heater in datas.water_heaters:
        if water_heater.widget == DeviceType.WATER_HEATER:
            devices.append(StandaloneCozytouchWaterHeater(water_heater))
        elif water_heater.widget == DeviceType.APC_WATER_HEATER:
            devices.append(StandaloneCozytouchAPCWaterHeater(water_heater))

    _LOGGER.info("Found %i water heater", len(devices))
    async_add_entities(devices, True)

    async def async_service_away_mode(service):
        """Handle away mode service."""
        entity_id = service.data.get(ATTR_ENTITY_ID)
        for device in devices:
            if device.entity_id == entity_id:
                await hass.async_add_executor_job(
                    device.async_set_away_mode, service.data[ATTR_TIME_PERIOD]
                )

    async def async_service_boost_mode(service):
        """Handle away mode service."""
        entity_id = service.data.get(ATTR_ENTITY_ID)
        for device in devices:
            if device.entity_id == entity_id:
                await hass.async_add_executor_job(
                    device.async_set_boost_mode, service.data[ATTR_TIME_PERIOD]
                )

    hass.services.async_register(
        DOMAIN, SERVICE_SET_AWAY_MODE, async_service_away_mode, schema=AWAY_MODE_SCHEMA
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_BOOST_MODE,
        async_service_boost_mode,
        schema=BOOST_MODE_SCHEMA,
    )


class StandaloneCozytouchWaterHeater(WaterHeaterEntity):
    """Representation a Water Heater."""

    COZY_TO_HASS_STATE = {
        "manualEcoActive": STATE_ECO,
        "manualEcoInactive": STATE_MANUEL,
        "autoMode": STATE_AUTO,
    }

    HASS_TO_COZY_STATE = {
        STATE_ECO: "manualEcoActive",
        STATE_MANUEL: "manualEcoInactive",
        STATE_AUTO: "autoMode",
    }

    SUPPORT_WATER_HEATER = [
        STATE_ECO,
        STATE_AUTO,
        STATE_MANUEL,
    ]

    DEFAULT_MIN_TEMP = 50
    DEFAULT_MAX_TEMP = 62

    def __init__(self, water_heater):
        """Initialize the sensor."""
        self.water_heater = water_heater
        self._support_flags = None
        self._target_temperature = None
        self._away = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self.water_heater.name

    @property
    def unique_id(self):
        """Return the name of the sensor."""
        return self.water_heater.id

    def avaibility(self):
        """Return avaibility sensor."""
        return self.water_heater.is_on

    @property
    def target_temperature_high(self):
        """Return the highbound target temperature we try to reach."""
        return self.water_heater.get_state(
            DeviceState.MAX_TEMPERATURE_MANUEL_MODE_STATE
        )

    @property
    def target_temperature_low(self):
        """Return the lowbound target temperature we try to reach."""
        return self.water_heater.get_state(
            DeviceState.MIN_TEMPERATURE_MANUEL_MODE_STATE
        )

    @property
    def min_temp(self):
        """Return the minimum temperature."""
        return self.DEFAULT_MIN_TEMP

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        return self.DEFAULT_MAX_TEMP

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return SUPPORT_OPERATION_MODE | SUPPORT_AWAY_MODE | SUPPORT_TARGET_TEMPERATURE

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def current_operation(self):
        """Return current operation ie. eco, electric, performance, ..."""
        return self.COZY_TO_HASS_STATE[self.water_heater.operating_mode]

    @property
    def operation_list(self):
        """List of available operation modes."""
        return self.SUPPORT_WATER_HEATER

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self.water_heater.current_temperature

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self.water_heater.target_temperature

    @property
    def is_away_mode_on(self):
        """Return true if away mode is on."""
        return self.water_heater.is_away_mode

    @property
    def is_boost_mode_on(self):
        """Return true if boost mode is on."""
        return self.water_heater.is_boost_mode

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "name": self.name,
            "identifiers": {(DOMAIN, self.unique_id)},
            "manufacturer": self.water_heater.manufacturer,
            "model": self.water_heater.get_state(DeviceState.DHW_CAPACITY_STATE),
            "via_device": (DOMAIN, self.water_heater.data["placeOID"]),
        }

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        attributes = {
            "energy_demand": self.water_heater.get_state(
                DeviceState.OPERATING_MODE_CAPABILITIES_STATE, {}
            ).get("energyDemandStatus")
            == 1,
            "away_mode_duration": self.water_heater.get_state(
                DeviceState.AWAY_MODE_DURATION_STATE
            ),
            "boost_mode": self.is_boost_mode_on,
            "boost_mode_duration": self.water_heater.get_state(
                DeviceState.BOOST_MODE_DURATION_STATE
            ),
            "boost_mode_start": self.water_heater.get_state(
                DeviceState.BOOST_START_DATE_STATE
            ),
            "boost_mode_end": self.water_heater.get_state(
                DeviceState.BOOST_END_DATE_STATE
            ),
            "anti_legionellosis": self.water_heater.get_state(
                DeviceState.ANTI_LEGIONELLOSIS_STATE
            ),
            "programmation": self.water_heater.get_state(
                DeviceState.PROGRAMMING_SLOTS_STATE
            ),
            "V40": self.water_heater.get_state(
                DeviceState.V40_WATER_VOLUME_ESTIMATION_STATE
            ),
            "booster_time": int(
                self.water_heater.get_state(
                    DeviceState.ELECTRIC_BOOSTER_OPERATING_TIME_STATE
                )
                or -1
            ),
            "heatpump_time": int(
                self.water_heater.get_state(DeviceState.HEAT_PUMP_OPERATING_TIME_STATE)
                or -1
            ),
            "showers_remaining": int(
                self.water_heater.get_state(DeviceState.NUM_SHOWER_REMAINING_STATE)
                or -1
            ),
            "power_electrical": int(
                self.water_heater.get_state(DeviceState.POWER_HEAT_ELECTRICAL_STATE)
            )
            / 1000,
            "power_heatpump": int(
                self.water_heater.get_state(DeviceState.POWER_HEAT_PUMP_STATE)
            )
            / 1000,
            "efficiency": round(
                (
                    int(
                        self.water_heater.get_state(
                            DeviceState.HEAT_PUMP_OPERATING_TIME_STATE
                        )
                    )
                    / (
                        int(
                            self.water_heater.get_state(
                                DeviceState.ELECTRIC_BOOSTER_OPERATING_TIME_STATE
                            )
                        )
                        + int(
                            self.water_heater.get_state(
                                DeviceState.HEAT_PUMP_OPERATING_TIME_STATE
                            )
                        )
                    )
                )
                * 100
            ),
        }

        # Remove attributes is empty
        clean_attributes = {
            k: v for k, v in attributes.items() if (v is not None and v != -1)
        }
        return clean_attributes

    async def async_set_operation_mode(self, operation_mode):
        """Set new target operation mode."""
        await self.water_heater.set_operating_mode(
            self.HASS_TO_COZY_STATE[operation_mode]
        )

    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""
        self._target_temperature = kwargs.get(ATTR_TEMPERATURE)
        await self.water_heater.set_temperature(self._target_temperature)

    async def async_set_away_mode(self, period):
        """Turn away on."""
        _LOGGER.debug("Set away mode for %i days", period)
        await self.water_heater.set_away_mode(period)

    async def async_set_boost_mode(self, period):
        """Turn away on."""
        _LOGGER.debug("Set boost mode for %i days", period)
        await self.water_heater.set_boost_mode(period)

    async def async_turn_boost_mode_on(self):
        """Turn boost on (7 days max)."""
        _LOGGER.debug("Turn off boost mode")
        await self.async_set_boost_mode(7)

    async def async_turn_boost_mode_off(self):
        """Turn away off."""
        _LOGGER.debug("Turn off boost mode")
        await self.async_set_boost_mode(0)

    async def async_turn_away_mode_on(self):
        """Turn away on (99 days max)."""
        _LOGGER.debug("Turn on away mode")
        await self.async_set_away_mode(99)

    async def async_turn_away_mode_off(self):
        """Turn away off."""
        _LOGGER.debug("Turn off away mode")
        await self.async_set_away_mode(0)

    async def async_update(self):
        """Fetch new state data for this sensor."""
        _LOGGER.debug("Update water heater %s", self.name)
        try:
            await self.water_heater.update()
        except CozytouchException:
            _LOGGER.error("Device data no retrieve %s", self.name)


class StandaloneCozytouchAPCWaterHeater(WaterHeaterEntity):
    """Representation a Water Heater."""

    COZY_TO_HASS_STATE = {
        "eco": STATE_ECO,
        "comfort": STATE_COMFORT,
        "manu": STATE_MANUEL,
        "auto": STATE_AUTO,
        "stop": STATE_OFF,
        "internalScheduling": STATE_ON,
        "externalScheduling": STATE_EXTERNAL,
    }

    HASS_TO_COZY_STATE = {
        STATE_ECO: "eco",
        STATE_COMFORT: "comfort",
        STATE_MANUEL: "manu",
        STATE_AUTO: "auto",
        STATE_OFF: "stop",
        STATE_ON: "internalScheduling",
        STATE_EXTERNAL: "externalScheduling",
    }

    SUPPORT_WATER_HEATER = [
        STATE_ECO,
        STATE_AUTO,
        STATE_MANUEL,
        STATE_COMFORT,
        STATE_OFF,
        STATE_ON,
        STATE_EXTERNAL,
    ]

    DEFAULT_MIN_TEMP = 40
    DEFAULT_MAX_TEMP = 45

    def __init__(self, water_heater):
        """Initialize the sensor."""
        self.water_heater = water_heater
        self._support_flags = None
        self._target_temperature = None
        self._away = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self.water_heater.name

    @property
    def unique_id(self):
        """Return the name of the sensor."""
        return self.water_heater.id

    def avaibility(self):
        """Return avaibility sensor."""
        return self.water_heater.is_on

    @property
    def target_temperature_high(self):
        """Return the highbound target temperature we try to reach."""
        return self.water_heater.get_state(
            DeviceState.COMFORT_TARGET_DHW_TEMPERATURE_STATE
        )

    @property
    def target_temperature_low(self):
        """Return the lowbound target temperature we try to reach."""
        return self.water_heater.get_state(DeviceState.ECO_TARGET_DHW_TEMPERATURE_STATE)

    @property
    def min_temp(self):
        """Return the minimum temperature."""
        return self.DEFAULT_MIN_TEMP

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        return self.DEFAULT_MAX_TEMP

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return SUPPORT_OPERATION_MODE | SUPPORT_AWAY_MODE | SUPPORT_TARGET_TEMPERATURE

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def current_operation(self):
        """Return current operation ie. eco, electric, performance, ..."""
        return self.COZY_TO_HASS_STATE[self.water_heater.operating_mode]

    @property
    def operation_list(self):
        """List of available operation modes."""
        return self.SUPPORT_WATER_HEATER

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self.water_heater.current_temperature

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self.water_heater.target_temperature

    @property
    def is_away_mode_on(self):
        """Return true if away mode is on."""
        return self.water_heater.is_away_mode

    @property
    def is_boost_mode_on(self):
        """Return true if boost mode is on."""
        return self.water_heater.is_boost_mode

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "name": self.name,
            "identifiers": {(DOMAIN, self.unique_id)},
            "manufacturer": self.water_heater.manufacturer,
            "model": self.water_heater.get_state(DeviceState.DHW_CAPACITY_STATE),
            "via_device": (DOMAIN, self.water_heater.data["placeOID"]),
        }

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        attributes = {
            "energy_demand": self.water_heater.get_state(
                DeviceState.OPERATING_MODE_CAPABILITIES_STATE, {}
            ).get("energyDemandStatus")
            == 1,
            "away_mode_duration": self.water_heater.get_state(
                DeviceState.AWAY_MODE_DURATION_STATE
            ),
            "boost_mode": self.is_boost_mode_on,
            "boost_mode_duration": self.water_heater.get_state(
                DeviceState.BOOST_MODE_DURATION_STATE
            ),
            "boost_mode_start": self.water_heater.get_state(
                DeviceState.BOOST_START_DATE_STATE
            ),
            "boost_mode_end": self.water_heater.get_state(
                DeviceState.BOOST_END_DATE_STATE
            ),
            "anti_legionellosis": self.water_heater.get_state(
                DeviceState.ANTI_LEGIONELLOSIS_STATE
            ),
            "programmation": self.water_heater.get_state(
                DeviceState.PROGRAMMING_SLOTS_STATE
            ),
            "V40": self.water_heater.get_state(
                DeviceState.V40_WATER_VOLUME_ESTIMATION_STATE
            ),
            "booster_time": int(
                self.water_heater.get_state(
                    DeviceState.ELECTRIC_BOOSTER_OPERATING_TIME_STATE
                )
                or -1
            ),
            "heatpump_time": int(
                self.water_heater.get_state(DeviceState.HEAT_PUMP_OPERATING_TIME_STATE)
                or -1
            ),
            "showers_remaining": int(
                self.water_heater.get_state(DeviceState.NUM_SHOWER_REMAINING_STATE)
                or -1
            ),
        }

        # Remove attributes is empty
        clean_attributes = {
            k: v for k, v in attributes.items() if (v is not None and v != -1)
        }
        return clean_attributes

    async def async_set_operation_mode(self, operation_mode):
        """Set new target operation mode."""
        await self.water_heater.set_operating_mode(
            self.HASS_TO_COZY_STATE[operation_mode]
        )

    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""
        _LOGGER.debug(kwargs)
        self._target_temperature = kwargs.get(ATTR_TEMPERATURE)
        await self.water_heater.set_temperature(self._target_temperature)

    async def async_set_away_mode(self, period):
        """Turn away on."""
        _LOGGER.debug("Set away mode for %i days", period)
        await self.water_heater.set_away_mode(period)

    async def async_turn_boost_mode_on(self):
        """Turn boost on (7 days max)."""
        _LOGGER.debug("Turn off boost mode")
        await self.water_heater.set_boost_mode(1)

    async def async_turn_boost_mode_off(self):
        """Turn away off."""
        _LOGGER.debug("Turn off boost mode")
        await self.water_heater.set_boost_mode(0)

    async def async_turn_away_mode_on(self):
        """Turn away on."""
        _LOGGER.debug("Turn on away mode")
        await self.async_set_away_mode(99)

    async def async_turn_away_mode_off(self):
        """Turn away off."""
        _LOGGER.debug("Turn off away mode")
        await self.async_set_away_mode(0)

    async def async_update(self):
        """Fetch new state data for this sensor."""
        _LOGGER.debug("Update water heater %s", self.name)
        try:
            await self.water_heater.update()
        except CozytouchException:
            _LOGGER.error("Device data no retrieve %s", self.name)
