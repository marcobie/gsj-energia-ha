from datetime import timedelta
import logging

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.core import HomeAssistant

from .api import GSJClient
from .const import DOMAIN, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class GSJEnergiaCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, client: GSJClient, scan_interval: int = DEFAULT_SCAN_INTERVAL):
        self.client = client

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self):
        try:
            return await self.client.get_status()
        except Exception as err:
            raise UpdateFailed(f"Błąd komunikacji z GSJ Browser API: {err}") from err
