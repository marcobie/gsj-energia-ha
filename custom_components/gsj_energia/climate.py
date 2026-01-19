from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.const import UnitOfTemperature

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([GSJClimate(coordinator)])


class GSJClimate(ClimateEntity):
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_name = "GSJ CO"
        self._attr_unique_id = "gsj_co_climate"
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        self._attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
        self._attr_hvac_modes = [HVACMode.HEAT, HVACMode.OFF]

    @property
    def current_temperature(self):
        return self.coordinator.data.get("temperatura_zew")

    @property
    def target_temperature(self):
        return self.coordinator.data.get("co_zadana")

    @property
    def hvac_mode(self):
        return HVACMode.HEAT if self.coordinator.data.get("co_status") == 1 else HVACMode.OFF

    async def async_set_temperature(self, **kwargs):
        temperature = kwargs.get("temperature")
        if temperature is not None:
            await self.coordinator.api.set_value("CO_ZADANA", temperature)
            await self.coordinator.async_request_refresh()
