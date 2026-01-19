from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS
from .api import GSJClient
from .coordinator import GSJEnergiaCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    host = entry.data["host"]
    port = entry.data["port"]
    device_id = entry.data["device_id"]

    client = GSJClient(host, port, device_id)
    coordinator = GSJEnergiaCoordinator(hass, client)

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    hass.data[DOMAIN].pop(entry.entry_id)
    return True
