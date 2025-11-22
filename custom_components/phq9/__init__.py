"""The PHQ-9 integration."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up PHQ-9 from a config entry."""

    phq9_hass_data = hass.data.setdefault(DOMAIN, {})

    entity_registry = er.async_get(hass)

    def entity_registry_listener(event):
        """Handle entity registry updates."""
        if event.data["action"] == "create" and event.data["entity_id"].startswith("person."):
            hass.async_create_task(hass.config_entries.async_reload(entry.entry_id))
        elif event.data["action"] == "remove" and event.data["entity_id"].startswith("person."):
            hass.async_create_task(hass.config_entries.async_reload(entry.entry_id))

    phq9_hass_data["entity_registry_listener"] = hass.bus.async_listen(
        er.EVENT_ENTITY_REGISTRY_UPDATED, entity_registry_listener
    )

    await hass.config_entries.async_forward_entry_setups(entry, ["select", "sensor"])

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""

    if listener := hass.data[DOMAIN].pop("entity_registry_listener", None):
        listener()

    return await hass.config_entries.async_unload_platforms(entry, ["select", "sensor"])

"""
Kroenke K, Spitzer RL, Williams JB. The PHQ-9: validity of a brief depression severity measure. J Gen Intern Med. 2001 Sep;16(9):606-13. doi: 10.1046/j.1525-1497.2001.016009606.x. PMID: 11556941; PMCID: PMC1495268.
"""
