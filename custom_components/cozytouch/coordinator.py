"""Helpers to help coordinate updates."""
from datetime import timedelta
import logging
from typing import Optional

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from cozytouchpy.client import CozytouchClient
from cozytouchpy.exception import AuthentificationFailed, CozytouchException

_LOGGER = logging.getLogger(__name__)


class CozytouchDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from Cozytouch platform."""

    def __init__(
        self,
        hass: HomeAssistant,
        logger: logging.Logger,
        *,
        name: str,
        client: CozytouchClient,
        update_interval: Optional[timedelta] = None,
        config_entry_id: str,
    ):
        """Initialize global data updater."""
        super().__init__(
            hass,
            logger,
            name=name,
            update_interval=update_interval,
        )

        self.data = {}
        self.client = client
        self._config_entry_id = config_entry_id

    async def _async_update_data(self):
        """Fetch Cozytouch data via event listener."""
        try:
            await self.client.connect()
            self.data = await self.client.get_setup()
        except AuthentificationFailed as exception:
            raise ConfigEntryAuthFailed() from exception
        except CozytouchException as exception:
            raise UpdateFailed("Too many requests, try again later.") from exception
        except Exception as exception:
            _LOGGER.debug(exception)
            raise UpdateFailed(exception) from exception

        return self.data
