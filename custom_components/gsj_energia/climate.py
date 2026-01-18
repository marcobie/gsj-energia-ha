from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import HVACMode, HVACAction
from homeassistant.const import UnitOfTemperature

from .const import DOMAIN


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    data = hass.data[DOMAIN]
    coordinator = data["coordinator"]
    client = data["client"]

    async_add_entities([GSJClimateCO(coordinator, client)])


class GSJClimateCO(ClimateEntity):
    def __init__(self, coordinator, client):
        self.coordinator = coordinator
        self.client = client
        self._attr_name = "GSJ CO"
        self._attr_unique_id = "gsj_co_climate"

    @property
    def supported_features(self):
        return 1  # temperature

    @property
    def temperature_unit(self):
        return UnitOfTemperature.CELSIUS

    @property
    def hvac_modes(self):
        return [HVACMode.OFF, HVACMode.HEAT]

    @property
    def hvac_mode(self):
        status = str(self.coordinator.data.get("CO_STATUS", "0"))
        return HVACMode.HEAT if status == "1" else HVACMode.OFF

    @property
    def hvac_action(self):
        compressor = str(self.coordinator.data.get("SSH_TRYG", "0"))
        return HVACAction.HEATING if compressor == "1" else HVACAction.IDLE

    @property
    def current_temperature(self):
        try:
            return float(self.coordinator.data.get("TEMPERATURA_ZASIL"))
        except Exception:
            return None

    @property
    def target_temperature(self):
        try:
            return float(self.coordinator.data.get("GRZANIE_ZADANA"))
        except Exception:
            return None

    async def async_set_temperature(self, **kwargs):
        temperature = kwargs.get("temperature")
        if temperature is not None:
            await self.client.set_value("GRZANIE_ZADANA", temperature)
            await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode):
        value = 1 if hvac_mode == HVACMode.HEAT else 0
        await self.client.set_value("CO_STATUS", value)
        await self.coordinator.async_request_refresh()

    async def async_update(self):
        await self.coordinator.async_request_refresh()
