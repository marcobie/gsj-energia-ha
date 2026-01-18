from homeassistant.components.sensor import SensorEntity
from homeassistant.const import UnitOfTemperature

from .const import DOMAIN


SENSORS = {
    "TEMPERATURA_ZASIL": "GSJ Temperatura zasilania",
    "TEMPERATURA_BUFOR": "GSJ Temperatura bufora",
    "TEMPERATURA_CWU": "GSJ Temperatura CWU",
    "TEMPERATURA_ZEWN": "GSJ Temperatura zewnętrzna",
    "TEMP_PAROWNIKA": "GSJ Temperatura parownika",
    "TEMP_GAZ_PAROWANIE": "GSJ Temperatura gazu (parowanie)",
}


async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]

    entities = [
        GSJTemperatureSensor(coordinator, key, name)
        for key, name in SENSORS.items()
    ]

    async_add_entities(entities)


class GSJTemperatureSensor(SensorEntity):
    def __init__(self, coordinator, key, name):
        self.coordinator = coordinator
        self.key = key
        self._attr_name = name
        self._attr_unique_id = f"gsj_{key.lower()}"

    @property
    def native_unit_of_measurement(self):
        return UnitOfTemperature.CELSIUS

    @property
    def native_value(self):
        try:
            return float(self.coordinator.data.get(self.key))
        except Exception:
            return None

    async def async_update(self):
        await self.coordinator.async_request_refresh()
