from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import GSJClient
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class GSJDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, client: GSJClient, update_interval: int = 60):
        self.client = client

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval),
        )

    async def _async_update_data(self):
        try:
            data = await self.client.get_status()
            _LOGGER.debug("Pobrane dane z GSJ Browser API: %s", data)
            return data
        except Exception as err:
            raise UpdateFailed(f"Błąd komunikacji z GSJ Browser API: {err}") from err
