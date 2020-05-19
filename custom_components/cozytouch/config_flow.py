"""Config flow to configure Cozytouch."""
import logging
import voluptuous as vol

from cozytouchpy.exception import CozytouchException, AuthentificationFailed

from homeassistant import config_entries, core
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD, CONF_TIMEOUT

from .const import DOMAIN, DEFAULT_TIMEOUT
from . import async_connect

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): int,
    }
)

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: core.HomeAssistant, data):
    """Validate the user input allows us to connect.

    Data has the keys from DATA_SCHEMA with values provided by the user.
    """
    return await async_connect(hass, data)


class CozytouchFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a Cozytouch config flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_import(self, import_config):
        """Import a config entry from configuration.yaml."""
        return await self.async_step_user(import_config)

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        errors = {}
        if user_input is not None:
            try:
                await validate_input(self.hass, user_input)
            except AuthentificationFailed as e:
                errors = {"base": "login_inccorect"}
                _LOGGER.error("Error: %s", e)
            except CozytouchException as e:
                errors = {"base": "parsing"}
                _LOGGER.error("Error: %s", e)

            if "base" not in errors:
                return self.async_create_entry(title="Cozytouch", data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )
