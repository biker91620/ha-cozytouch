"""Config flow to configure Cozytouch."""
import logging
import voluptuous as vol

from cozytouchpy import CozytouchClient, CozytouchException

from homeassistant import config_entries, core
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD, CONF_TIMEOUT

from .const import DOMAIN, DEFAULT_TIMEOUT

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

    try:
        CozytouchClient(data[CONF_USERNAME], data[CONF_PASSWORD], data[CONF_TIMEOUT])
    except CozytouchException as excpt:
        raise CozytouchException(excpt)


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
            except CozytouchException as excpt:
                errors = {"base": "login_inccorect"}
                _LOGGER.error("Error: {}".format(excpt))
            except Exception as excpt:
                errors = {"base": "unknown"}
                _LOGGER.error("Error: {}".format(excpt))

            if "base" not in errors:
                return self.async_create_entry(title="Cozytouch", data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )
