"""Sensors for Cozytouch."""
import logging

from cozytouchpy import CozytouchException
from cozytouchpy.constant import DeviceType, DeviceState

from homeassistant.const import TEMP_CELSIUS
from homeassistant.helpers.entity import Entity

from .const import COZYTOUCH_DATAS, DOMAIN, KW_UNIT

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set the sensor platform."""
    datas = hass.data[DOMAIN][config_entry.entry_id][COZYTOUCH_DATAS]

    devices = []
    for heater in datas.heaters:
        for sensor in heater.sensors:
            if sensor.widget == DeviceType.TEMPERATURE:
                devices.append(CozyTouchTemperatureSensor(sensor, heater))
            elif sensor.widget == DeviceType.ELECTRECITY:
                devices.append(CozyTouchElectricitySensor(sensor, heater))

    for water_heater in datas.water_heaters:
        for sensor in water_heater.sensors:
            if sensor.widget == DeviceType.TEMPERATURE:
                devices.append(CozyTouchTemperatureSensor(sensor, water_heater))
            elif sensor.widget == DeviceType.ELECTRECITY:
                devices.append(CozyTouchElectricitySensor(sensor, water_heater))

    for boiler in datas.boilers:
        devices.append(CozytouchBoiler(boiler))

    _LOGGER.info("Found {count} sensors".format(count=len(devices)))
    async_add_entities(devices, True)


class CozyTouchTemperatureSensor(Entity):
    """Representation of a temperature sensor."""

    def __init__(self, sensor, device):
        """Initialize temperature sensor."""
        self.sensor = sensor
        self.ref_id = device.id
        self.ref_name = device.name
        self.ref_manufacturer = device.manufacturer

    @property
    def unique_id(self):
        """Return the unique id of this sensor."""
        return self.sensor.id

    @property
    def name(self):
        """Return the display name of this sensor."""
        return "{place} {sensor}".format(
            place=self.sensor.place.name, sensor=self.sensor.name
        )

    @property
    def state(self):
        """Return the temperature."""
        return self.sensor.temperature

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    async def async_update(self):
        """Fetch new state data for this sensor."""
        _LOGGER.debug("Update sensor {name}".format(name=self.name))
        try:
            await self.sensor.update()
        except CozytouchException:
            _LOGGER.error("Device data no retrieve {}".format(self.name))

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "name": self.ref_name,
            "identifiers": {(DOMAIN, self.ref_id)},
            "manufacturer": self.ref_manufacturer,
            "via_device": (DOMAIN, self.sensor.data["placeOID"]),
        }


class CozyTouchElectricitySensor(Entity):
    """Representation of an electricity Sensor."""

    def __init__(self, sensor, device):
        """Initialize the sensor."""
        self.sensor = sensor
        self.ref_id = device.id
        self.ref_name = device.name
        self.ref_manufacturer = device.manufacturer

    @property
    def unique_id(self):
        """Return the unique id of this sensor."""
        return self.sensor.id

    @property
    def name(self):
        """Return the display name of this sensor."""
        return "{place} {sensor}".format(
            place=self.sensor.place.name, sensor=self.sensor.name
        )

    @property
    def state(self):
        """Return the electricity consumption."""
        return self.sensor.consumption / 1000

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return KW_UNIT

    async def async_update(self):
        """Fetch new state data for this sensor."""
        _LOGGER.debug("Update sensor {name}".format(name=self.name))
        try:
            await self.sensor.update()
        except CozytouchException:
            _LOGGER.error("Device data no retrieve {}".format(self.name))

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "name": self.ref_name,
            "identifiers": {(DOMAIN, self.ref_id)},
            "manufacturer": self.ref_manufacturer,
            "via_device": (DOMAIN, self.sensor.data["placeOID"]),
        }


class CozytouchBoiler(Entity):
    """Representation of an boiler Sensor."""

    def __init__(self, device):
        """Initialize the sensor."""
        self.boiler = device

    @property
    def unique_id(self):
        """Return the unique id of this sensor."""
        return self.boiler.id

    @property
    def name(self):
        """Return the display name of this sensor."""
        return self.boiler.name

    def avaibility(self):
        """Return avaibility sensor."""
        return self.boiler.get_state(DeviceState.STATUS_STATE) == "available"

    @property
    def state(self):
        """Return current operation ie. eco, electric, performance, ..."""
        return self.boiler.get_state(DeviceState.PASS_APC_OPERATING_MODE_STATE)

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "name": self.name,
            "identifiers": {(DOMAIN, self.unique_id)},
            "manufacturer": self.boiler.manufacturer,
            "model": self.boiler.get_state(DeviceState.PRODUCT_MODEL_NAME_STATE),
            "via_device": (DOMAIN, self.boiler.data["placeOID"]),
        }

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        attributes = {
            "programmation": self.boiler.timeprogram_state(),
            "away_target_temperature": self.boiler.away_target_temperature(),
            "error": self.boiler.get_state(DeviceState.ERROR_CODE_STATE),
        }

        # Remove attributes is empty
        clean_attributes = {
            k: v for k, v in attributes.items() if (v is not None and v != -1)
        }
        return clean_attributes

    async def async_update(self):
        """Fetch new state data for this sensor."""
        _LOGGER.debug("Update boiler {name}".format(name=self.name))
        try:
            await self.boiler.update()
        except CozytouchException:
            _LOGGER.error("Device data no retrieve {}".format(self.name))
