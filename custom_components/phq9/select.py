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

from .const import DOMAIN, PHQ9_ANSWERS

_LOGGER = logging.getLogger(__name__)

PHQ9_QUESTIONS = [
    "Little interest or pleasure in doing things",
    "Feeling down, depressed, or hopeless",
    "Trouble falling or staying asleep, or sleeping too much",
    "Feeling tired or having little energy",
    "Poor appetite or overeating",
    "Feeling bad about yourself - or that you are a failure or have let yourself or your family down",
    "Trouble concentrating on things, such as reading the newspaper or watching television",
    "Moving or speaking so slowly that other people could have noticed? Or the opposite - being so fidgety or restless that you have been moving around a lot more than usual",
    "Thoughts that you would be better off dead or of hurting yourself in some way",
]

DIFFICULTY_QUESTION = "If you checked off any problems, how difficult have these problems made it for you to do your work, take care of things at home, or get along with other people?"
DIFFICULTY_ANSWERS = [
    "Not difficult at all",
    "Somewhat difficult",
    "Very difficult",
    "Extremely difficult",
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the PHQ-9 input selects."""

    entity_registry = er.async_get(hass)

    person_entities = [
        entry for entry in entity_registry.entities.values() if entry.domain == "person"
    ]

    entities = []
    for person_entity in person_entities:
        device_info = DeviceInfo(
            identifiers={(DOMAIN, person_entity.unique_id)},
            name=person_entity.name,
            entry_type=dr.DeviceEntryType.SERVICE,
        )

        for i, question in enumerate(PHQ9_QUESTIONS):
            entities.append(
                PHQ9QuestionSelect(
                    hass,
                    person_entity,
                    device_info,
                    f"phq9_{person_entity.unique_id}_{i+1}",
                    f"{PHQ9_QUESTIONS[i]} {person_entity.name}",
                    question,
                    PHQ9_ANSWERS,
                )
            )

        entities.append(
            PHQ9QuestionSelect(
                hass,
                person_entity,
                device_info,
                f"phq9_{person_entity.unique_id}_difficulty",
                f"{DIFFICULTY_QUESTION} {person_entity.name}",
                DIFFICULTY_QUESTION,
                DIFFICULTY_ANSWERS,
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
        name: str,
        question: str,
        options: list[str],
    ):
        """Initialize the input select."""
        self.hass = hass
        self._person_entity = person_entity
        self._attr_device_info = device_info
        self._attr_unique_id = unique_id
        self._attr_name = name
        self._question = question
        self._attr_options = options
        self._attr_current_option = options[0] if options else None

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "question": self._question,
            "person_entity_id": self._person_entity.entity_id,
        }

    async def async_select_option(self, option: str) -> None:
        """Update the current option."""
        self._attr_current_option = option
        self.async_write_ha_state()
