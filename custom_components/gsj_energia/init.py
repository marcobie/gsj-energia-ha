import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.discovery import async_load_platform

from .api import GSJClient
from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_DEVICE_ID,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
)
from .coordinator import GSJDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    if DOMAIN not in config:
        return True

    conf = config[DOMAIN]

    host = conf[CONF_HOST]
    username = conf[CONF_USERNAME]
    password = conf[CONF_PASSWORD]
    device_id = conf[CONF_DEVICE_ID]
    scan_interval = conf.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

    client = GSJClient(host, username, password, device_id)
    await client.login()

    coordinator = GSJDataUpdateCoordinator(hass, client, scan_interval)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN] = {
        "client": client,
        "coordinator": coordinator,
    }

    # W następnych krokach doładujemy platformy:
    await async_load_platform(hass, "climate", DOMAIN, {}, config)
    await async_load_platform(hass, "sensor", DOMAIN, {}, config)
    await async_load_platform(hass, "binary_sensor", DOMAIN, {}, config)
    await async_load_platform(hass, "switch", DOMAIN, {}, config)
    await async_load_platform(hass, "number", DOMAIN, {}, config)

    _LOGGER.info("GSJ Energia coordinator uruchomiony (odświeżanie co %s s)", scan_interval)

    return True
