from homeassistant.components.binary_sensor import BinarySensorEntity

from .const import DOMAIN


BINARY_SENSORS = {
    "ALARM": "GSJ Alarm",
    "SSH_TRYG": "GSJ Sprężarka pracuje",
    "CO_STATUS": "GSJ CO aktywne",
    "CWU_STATUS": "GSJ CWU aktywne",
}


async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]

    entities = [
        GSJBinarySensor(coordinator, key, name)
        for key, name in BINARY_SENSORS.items()
    ]

    async_add_entities(entities)


class GSJBinarySensor(BinarySensorEntity):
    def __init__(self, coordinator, key, name):
        self.coordinator = coordinator
        self.key = key
        self._attr_name = name
        self._attr_unique_id = f"gsj_{key.lower()}"

    @property
    def is_on(self):
        return str(self.coordinator.data.get(self.key, "0")) == "1"

    async def async_update(self):
        await self.coordinator.async_request_refresh()
