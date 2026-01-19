from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import GSJDataUpdateCoordinator


@dataclass
class GSJSensorDescription:
    key: str
    name: str
    unit: str
    device_class: SensorDeviceClass | None = None


SENSORS: list[GSJSensorDescription] = [
    GSJSensorDescription(
        key="temperatura_zew",
        name="Temperatura zewnętrzna",
        unit="°C",
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    GSJSensorDescription(
        key="temperatura_cwu",
        name="Temperatura CWU",
        unit="°C",
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    GSJSensorDescription(
        key="temperatura_bufor",
        name="Temperatura bufora",
        unit="°C",
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    GSJSensorDescription(
        key="temp_parownik",
        name="Temperatura parownika",
        unit="°C",
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    GSJSensorDescription(
        key="temp_gaz_parowanie",
        name="Temperatura gazu parowania",
        unit="°C",
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: GSJDataUpdateCoordinator = data["coordinator"]

    entities: list[SensorEntity] = []

    for description in SENSORS:
        entities.append(GSJSensor(coordinator, description))

    async_add_entities(entities)


class GSJSensor(CoordinatorEntity[GSJDataUpdateCoordinator], SensorEntity):
    def __init__(self, coordinator: GSJDataUpdateCoordinator, description: GSJSensorDescription) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_name = f"GSJ {description.name}"
        self._attr_unique_id = f"gsj_{description.key}"
        self._attr_native_unit_of_measurement = description.unit
        self._attr_device_class = description.device_class
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> Any:
        return self.coordinator.data.get(self.entity_description.key)
