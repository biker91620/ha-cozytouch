"""The cozytouch component."""
import logging
from datetime import timedelta
import voluptuous as vol

from cozypy.client import CozytouchClient

from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from homeassistant.helpers import config_validation as cv, device_registry as dr
from homeassistant.config_entries import SOURCE_IMPORT

from .const import DOMAIN, COMPONENTS

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_USERNAME): cv.string,
                vol.Required(CONF_PASSWORD): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass, config):
    """Load configuration for Cozytouch component."""

    if not hass.config_entries.async_entries(DOMAIN) and DOMAIN in config:
        cozytouch_config = config[DOMAIN]
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN, context={"source": SOURCE_IMPORT}, data=cozytouch_config
            )
        )

    return True

async def async_setup_entry(hass, config_entry):
    """Set up Cozytouch as config entry."""

    config = CozytouchClient(config_entry["username"], config_entry["password"], config_entry["timeout"])
    if config:
        device_registry = await dr.async_get_registry(hass)
        device_registry.async_get_or_create(
            config_entry_id=config_entry.entry_id,
            identifiers={(DOMAIN, config_entry.data["id"])},
            manufacturer=config["Manufacturer"],
            name=config["ProductClass"],
            model=config["ModelName"],
            sw_version=config["SoftwareVersion"],
        )

        for component in COMPONENTS:
            hass.async_create_task(
                hass.config_entries.async_forward_entry_setup(config_entry, component)
            )
        return True

    return False


async def async_unload_entry(hass, config_entry):
    """Unload a config entry."""

    for component in COMPONENTS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_unload(config_entry, component)
        )
    return True

