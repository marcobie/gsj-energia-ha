from homeassistant.components.number import NumberEntity

from .const import DOMAIN


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    data = hass.data[DOMAIN]
    coordinator = data["coordinator"]
    client = data["client"]

    async_add_entities([
        GSJSetpointNumber(coordinator, client, "GRZANIE_ZADANA", "GSJ CO temperatura"),
        GSJSetpointNumber(coordinator, client, "CWU_ZADANA", "GSJ CWU temperatura"),
    ])


class GSJSetpointNumber(NumberEntity):
    def __init__(self, coordinator, client, key, name):
        self.coordinator = coordinator
        self.client = client
        self.key = key
        self._attr_name = name
        self._attr_unique_id = f"gsj_{key.lower()}"

    @property
    def native_value(self):
        try:
            return float(self.coordinator.data.get(self.key))
        except Exception:
            return None

    @property
    def native_min_value(self):
        return 20

    @property
    def native_max_value(self):
        return 65

    @property
    def native_step(self):
        return 1

    async def async_set_native_value(self, value):
        await self.client.set_value(self.key, int(value))
        await self.coordinator.async_request_refresh()

    async def async_update(self):
        await self.coordinator.async_request_refresh()
