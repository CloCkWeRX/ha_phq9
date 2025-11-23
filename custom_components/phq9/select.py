"""Platform for PHQ-9 input selects.
Kroenke K, Spitzer RL, Williams JB. The PHQ-9: validity of a brief depression severity measure. J Gen Intern Med. 2001 Sep;16(9):606-13. doi: 10.1046/j.1525-1497.2001.016009606.x. PMID: 11556941; PMCID: PMC1495268.
"""
from __future__ import annotations
from typing import Iterable

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.translation import async_get_translations


from .const import DOMAIN, PHQ9_ANSWER_KEYS, DIFFICULTY_ANSWER_KEYS

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the PHQ-9 input selects."""

    translations = await async_get_translations(hass, "en", "component", [DOMAIN])

    phq9_answers = [
        translations[f"component.{DOMAIN}.entity.select.phq9_answers.state.{key}"] for key in PHQ9_ANSWER_KEYS
    ]
    difficulty_answers = [
        translations[f"component.{DOMAIN}.entity.select.difficulty_answers.state.{key}"] for key in DIFFICULTY_ANSWER_KEYS
    ]

    entity_registry = er.async_get(hass)

    person_entities = [
        entry for entry in entity_registry.entities.values() if entry.domain == "person"
    ]

    entities = []
    for person_entity in person_entities:
        device_info = DeviceInfo(
            identifiers={(DOMAIN, person_entity.unique_id)},
            name=f"PHQ-9 {person_entity.original_name}",
            entry_type=dr.DeviceEntryType.SERVICE,
        )

        for i in range(9):
            entities.append(
                PHQ9QuestionSelect(
                    hass,
                    person_entity,
                    device_info,
                    f"phq9_q{i+1}_{person_entity.unique_id}",
                    f"phq9_question_{i+1}",
                    phq9_answers,
                )
            )

        entities.append(
            PHQ9QuestionSelect(
                hass,
                person_entity,
                device_info,
                f"phq9_difficulty_{person_entity.unique_id}",
                "phq9_difficulty",
                difficulty_answers,
            )
        )

    async_add_entities(entities)


class PHQ9QuestionSelect(SelectEntity):
    """Representation of a PHQ-9 Question input select."""

    def __init__(
        self,
        hass: HomeAssistant,
        person_entity: er.RegistryEntry,
        device_info: DeviceInfo,
        unique_id: str,
        translation_key: str,
        options: list[str],
    ):
        """Initialize the input select."""
        self.hass = hass
        self._person_entity = person_entity
        self._attr_device_info = device_info
        self._attr_unique_id = unique_id
        self._attr_translation_key = translation_key
        self._attr_options = options
        self._attr_current_option = options[0] if options else None

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "person_entity_id": self._person_entity.entity_id,
        }

    async def async_select_option(self, option: str) -> None:
        """Update the current option."""
        self._attr_current_option = option
        self.async_write_ha_state()
