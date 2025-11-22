"""Platform for PHQ-9 sensors.

Kroenke K, Spitzer RL, Williams JB. The PHQ-9: validity of a brief depression severity measure. J Gen Intern Med. 2001 Sep;16(9):606-13. doi: 10.1046/j.1525-1497.2001.016009606.x. PMID: 11556941; PMCID: PMC1495268.
"""
from __future__ import annotations
import asyncio

import logging
from datetime import datetime

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.event import async_track_state_change

from .const import DOMAIN, SCORE_MAP

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the PHQ-9 sensors."""

    entity_registry = er.async_get(hass)

    person_entities = [
        entry for entry in entity_registry.entities.values() if entry.domain == "person"
    ]

    sensors = []
    for person_entity in person_entities:
        device_info = DeviceInfo(
            identifiers={(DOMAIN, person_entity.unique_id)},
            name=person_entity.name,
            entry_type=dr.DeviceEntryType.SERVICE,
        )

        sensors.append(
            PHQ9TotalScoreSensor(
                hass,
                person_entity,
                device_info,
                f"phq9_{person_entity.unique_id}_score",
            )
        )

        sensors.append(
            PHQ9LastEvaluatedSensor(
                hass,
                person_entity,
                device_info,
                f"phq9_{person_entity.unique_id}_last_evaluated",
            )
        )

        sensors.append(
            PHQ9ScoreInterpretationSensor(
                hass,
                person_entity,
                device_info,
                f"phq9_{person_entity.unique_id}_score_interpretation",
            )
        )

    async_add_entities(sensors)


class PHQ9TotalScoreSensor(SensorEntity):
    """Representation of a PHQ-9 Total Score sensor."""

    def __init__(
        self,
        hass: HomeAssistant,
        person_entity: er.RegistryEntry,
        device_info: DeviceInfo,
        unique_id: str,
    ):
        """Initialize the sensor."""
        self.hass = hass
        self._person_entity = person_entity
        self._attr_device_info = device_info
        self._attr_unique_id = unique_id
        self._attr_native_value = 0
        self._question_entity_ids = []
        self._attr_translation_key = "phq9_total_score"


    async def async_added_to_hass(self) -> None:
        """Register state change listener and discover entity IDs."""
        await super().async_added_to_hass()

        async def _find_question_entities_with_retry():
            """Find the question entities, retrying if necessary."""
            for attempt in range(30): # 30 attempts * 10 seconds = 5 minutes
                entity_registry = er.async_get(self.hass)
                self._question_entity_ids = []
                for i in range(9):
                    unique_id = f"phq9_{self._person_entity.unique_id}_{i+1}"
                    entity_id = entity_registry.async_get_entity_id("select", DOMAIN, unique_id)
                    if entity_id:
                        self._question_entity_ids.append(entity_id)

                if len(self._question_entity_ids) == 9:
                    self.async_on_remove(
                        async_track_state_change(
                            self.hass, self._question_entity_ids, self._async_update_score
                        )
                    )
                    self.hass.async_create_task(self._async_update_score(None, None, None))
                    return

                await asyncio.sleep(10)

            _LOGGER.error("Could not find all 9 PHQ-9 question entities for %s after multiple retries", self._person_entity.name)

        self.hass.async_create_task(_find_question_entities_with_retry())

    @callback
    async def _async_update_score(self, entity_id, old_state, new_state) -> None:
        """Update the total score."""
        score = 0
        for entity_id in self._question_entity_ids:
            state = self.hass.states.get(entity_id)
            if state:
                score += SCORE_MAP.get(state.state, 0)

        self._attr_native_value = score
        self.async_write_ha_state()


class PHQ9LastEvaluatedSensor(SensorEntity):
    """Representation of a PHQ-9 Last Evaluated sensor."""

    def __init__(
        self,
        hass: HomeAssistant,
        person_entity: er.RegistryEntry,
        device_info: DeviceInfo,
        unique_id: str,
    ):
        """Initialize the sensor."""
        self.hass = hass
        self._person_entity = person_entity
        self._attr_device_info = device_info
        self._attr_unique_id = unique_id
        self._attr_native_value = None
        self._all_question_entity_ids = []
        self._attr_translation_key = "phq9_last_evaluated"


    async def async_added_to_hass(self) -> None:
        """Register state change listener and discover entity IDs."""
        await super().async_added_to_hass()

        async def _find_question_entities_with_retry():
            """Find the question entities, retrying if necessary."""
            for attempt in range(30): # 30 attempts * 10 seconds = 5 minutes
                entity_registry = er.async_get(self.hass)
                self._all_question_entity_ids = []
                for i in range(9):
                    unique_id = f"phq9_{self._person_entity.unique_id}_{i+1}"
                    entity_id = entity_registry.async_get_entity_id("select", DOMAIN, unique_id)
                    if entity_id:
                        self._all_question_entity_ids.append(entity_id)

                difficulty_unique_id = f"phq9_{self._person_entity.unique_id}_difficulty"
                difficulty_entity_id = entity_registry.async_get_entity_id("select", DOMAIN, difficulty_unique_id)
                if difficulty_entity_id:
                    self._all_question_entity_ids.append(difficulty_entity_id)

                if len(self._all_question_entity_ids) == 10:
                    self.async_on_remove(
                        async_track_state_change(
                            self.hass, self._all_question_entity_ids, self._async_update_timestamp
                        )
                    )
                    return

                await asyncio.sleep(10)

            _LOGGER.error("Could not find all 10 PHQ-9 input entities for %s after multiple retries", self._person_entity.name)

        self.hass.async_create_task(_find_question_entities_with_retry())

    @callback
    async def _async_update_timestamp(self, entity_id, old_state, new_state) -> None:
        """Update the timestamp."""
        if old_state is not None and new_state is not None and old_state.state != new_state.state:
            self._attr_native_value = datetime.now().isoformat()
            self.async_write_ha_state()


class PHQ9ScoreInterpretationSensor(SensorEntity):
    """Representation of a PHQ-9 Score Interpretation sensor."""

    def __init__(
        self,
        hass: HomeAssistant,
        person_entity: er.RegistryEntry,
        device_info: DeviceInfo,
        unique_id: str,
    ):
        """Initialize the sensor."""
        self.hass = hass
        self._person_entity = person_entity
        self._attr_device_info = device_info
        self._attr_unique_id = unique_id
        self._attr_native_value = "none_minimal"
        self._total_score_entity_id = None
        self._attr_translation_key = "phq9_score_interpretation"


    async def async_added_to_hass(self) -> None:
        """Register state change listener."""
        await super().async_added_to_hass()

        async def _find_score_entity_with_retry():
            """Find the score entity, retrying if necessary."""
            for attempt in range(30): # 30 attempts * 10 seconds = 5 minutes
                entity_registry = er.async_get(self.hass)
                unique_id = f"phq9_{self._person_entity.unique_id}_score"
                self._total_score_entity_id = entity_registry.async_get_entity_id("sensor", DOMAIN, unique_id)

                if self._total_score_entity_id:
                    self.async_on_remove(
                        async_track_state_change(
                            self.hass, self._total_score_entity_id, self._async_update_interpretation
                        )
                    )
                    self.hass.async_create_task(self._async_update_interpretation(None, None, None))
                    return

                await asyncio.sleep(10)

            _LOGGER.error("Could not find total score entity for %s after multiple retries", self._person_entity.name)

        self.hass.async_create_task(_find_score_entity_with_retry())

    @callback
    async def _async_update_interpretation(self, entity_id, old_state, new_state) -> None:
        """Update the score interpretation."""
        state = self.hass.states.get(self._total_score_entity_id)
        if state and state.state is not None:
            try:
                score = int(state.state)
                if 0 <= score <= 4:
                    self._attr_native_value = "none_minimal"
                elif 5 <= score <= 9:
                    self._attr_native_value = "mild"
                elif 10 <= score <= 14:
                    self._attr_native_value = "moderate"
                elif 15 <= score <= 19:
                    self._attr_native_value = "moderately_severe"
                else: # 20 <= score <= 27:
                    self._attr_native_value = "severe"
                self.async_write_ha_state()
            except (ValueError, TypeError):
                self._attr_native_value = "unknown"
                self.async_write_ha_state()
