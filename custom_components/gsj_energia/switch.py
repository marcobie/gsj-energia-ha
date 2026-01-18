from homeassistant.components.switch import SwitchEntity

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    client = data["client"]

    async_add_entities([GSJCWUSwitch(coordinator, client)])


class GSJCWUSwitch(SwitchEntity):
    def __init__(self, coordinator, client):
        self.coordinator = coordinator
        self.client = client
        self._attr_name = "GSJ CWU"
        self._attr_unique_id = "gsj_cwu_switch"

    @property
    def is_on(self):
        return str(self.coordinator.data.get("CWU_STATUS", "0")) == "1"

    async def async_turn_on(self, **kwargs):
        await self.client.set_value("CWU_STATUS", 1)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        await self.client.set_value("CWU_STATUS", 0)
        await self.coordinator.async_request_refresh()

    async def async_update(self):
        await self.coordinator.async_request_refresh()
