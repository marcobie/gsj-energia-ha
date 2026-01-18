from datetime import timedelta
import logging

from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Lista kluczy, które cyklicznie odczytujemy z API
GSJ_KEYS = [
    "TEMPERATURA_ZASIL",
    "TEMPERATURA_BUFOR",
    "TEMPERATURA_CWU",
    "TEMPERATURA_ZEWN",
    "TEMP_PAROWNIKA",
    "TEMP_GAZ_PAROWANIE",
    "GRZANIE_ZADANA",
    "CWU_ZADANA",
    "CO_STATUS",
    "CWU_STATUS",
    "SSH_TRYG",
    "ALARM",
]


class GSJDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, client, scan_interval):
        self.client = client

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self):
        """Pobierz wszystkie dane z GSJ."""
        data = {}

        try:
            for key in GSJ_KEYS:
                value = await self.client.get_value(key)
                data[key] = value
            return data

        except Exception as err:
            raise UpdateFailed(f"Błąd komunikacji z GSJ: {err}") from err
