"""Sensors for Cozytouch."""
import logging

import voluptuous as vol
from cozytouchpy import CozytouchException
from cozytouchpy.constant import DeviceState, DeviceType
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import homeassistant.helpers.config_validation as cv
from homeassistant.const import ATTR_ENTITY_ID, ENERGY_KILO_WATT_HOUR
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import (
    STATE_CLASS_MEASUREMENT,
    STATE_CLASS_TOTAL_INCREASING,
    SensorEntity,
    DEVICE_CLASS_TEMPERATURE,
    TEMP_CELSIUS,
    DEVICE_CLASS_ENERGY,
)

from .const import (
    ATTR_OPERATION_MODE,
    DOMAIN,
    SERVICE_SET_OPERATION_MODE,
    COORDINATOR,
)

_LOGGER = logging.getLogger(__name__)

BOILER_OPERATION_MODE = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_id,
        vol.Required(ATTR_OPERATION_MODE): cv.string,
    }
)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set the sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]
    devices = []
    boilers_exists = False
    for sensor in coordinator.data.sensors.values():
        if sensor.widget == DeviceType.TEMPERATURE:
            devices.append(CozyTouchTemperatureSensor(sensor, coordinator))
        elif sensor.widget in [DeviceType.ELECTRICITY, DeviceType.DHW_ELECTRICITY]:
            devices.append(CozyTouchElectricitySensor(sensor, coordinator))

    for device in coordinator.data.devices.values():
        if device.widget == DeviceType.APC_BOILER:
            boilers_exists = True
            devices.append(CozytouchBoiler(device, coordinator))

    if boilers_exists:

        async def async_service_operation_mode(service):
            """Handle operation mode service."""
            entity_id = service.data.get(ATTR_ENTITY_ID)
            for device in devices:
                if device.entity_id == entity_id:
                    await device.async_set_operation_mode(
                        service.data[ATTR_OPERATION_MODE]
                    )

        hass.services.async_register(
            DOMAIN,
            SERVICE_SET_OPERATION_MODE,
            async_service_operation_mode,
            schema=BOILER_OPERATION_MODE,
        )
    async_add_entities(devices)


class CozyTouchSensor(CoordinatorEntity, SensorEntity):
    """Representation of a temperature sensor."""

    def __init__(self, device, coordinator):
        """Initialize temperature sensor."""
        super().__init__(coordinator)
        self.sensor = device
        self.ref_id = self.sensor.parent.id
        self.ref_name = self.sensor.parent.name
        self.ref_manufacturer = self.sensor.parent.manufacturer
        self.coordinator = coordinator
        self._native_value = None

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
    def device_info(self):
        """Return the device info."""
        return {
            "name": self.ref_name,
            "identifiers": {(DOMAIN, self.ref_id)},
            "manufacturer": self.ref_manufacturer,
            "via_device": (DOMAIN, self.sensor.data["placeOID"]),
        }


class CozyTouchTemperatureSensor(CozyTouchSensor):
    """Representation of a temperature sensor."""

    @property
    def device_class(self):
        """Return the device class."""
        return DEVICE_CLASS_TEMPERATURE

    @property
    def state_class(self):
        """Return the device class."""
        return STATE_CLASS_MEASUREMENT

    @property
    def native_value(self):
        """Return the temperature."""
        return self.coordinator.data.sensors[self.unique_id].temperature

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS


class CozyTouchElectricitySensor(CozyTouchSensor):
    """Representation of an electricity Sensor."""

    @property
    def device_class(self):
        """Return the device class."""
        return DEVICE_CLASS_ENERGY

    @property
    def state_class(self):
        """Return the device class."""
        return STATE_CLASS_TOTAL_INCREASING

    @property
    def native_value(self):
        """Return the electricity consumption."""
        return self.coordinator.data.sensors[self.unique_id].consumption / 1000

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return ENERGY_KILO_WATT_HOUR


class CozytouchBoiler(Entity):
    """Representation of an boiler Sensor."""

    def __init__(self, device, coordinator):
        """Initialize the sensor."""
        self.boiler = device
        self.coordinator = coordinator

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
        datas = self.coordinator.data.devices[self.unique_id]
        return datas.get_state(DeviceState.STATUS_STATE) == "available"

    @property
    def state(self):
        """Return current operation ie. eco, electric, performance, ..."""
        datas = self.coordinator.data.devices[self.unique_id]
        return datas.get_state(DeviceState.PASS_APC_OPERATING_MODE_STATE)

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
    def extra_state_attributes(self):
        """Return the device state attributes."""
        datas = self.coordinator.data.devices[self.unique_id]
        attributes = {
            "away_target_temperature": datas.away_target_temperature,
            "error": datas.get_state(DeviceState.ERROR_CODE_STATE),
            "programmation": datas.timeprogram_state,
        }

        # Remove attributes is empty
        clean_attributes = {
            k: v for k, v in attributes.items() if (v is not None and v != -1)
        }
        return clean_attributes

    async def async_set_operation_mode(self, mode):
        """Set operation mode."""
        try:
            await self.boiler.async_set_operation_mode(mode)
        except CozytouchException as excpt:
            _LOGGER.error("Error for set operation %s", excpt)
