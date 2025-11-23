"""Tests for the phq9 sensor platform."""

from unittest.mock import patch

from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from homeassistant.components.person import async_setup
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from homeassistant.config_entries import ConfigEntryState

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.phq9.const import DOMAIN

DOMAIN = "phq9"


async def test_sensors_created_for_person(hass: HomeAssistant) -> None:
    """Test that sensors are created for a person."""
    # Setup a mock person
    await async_setup_component(
        hass, "person", {"person": [{"name": "test", "id": "1234"}]}
    )
    hass.bus.async_fire(EVENT_HOMEASSISTANT_STARTED)
    await hass.async_block_till_done()

    entry = MockConfigEntry(domain=DOMAIN, data={})
    entry.add_to_hass(hass)

    with patch("asyncio.sleep", return_value=None):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.LOADED

    # Check that the sensors were created
    assert hass.states.get("sensor.phq_9_total_score") is not None
    assert hass.states.get("sensor.phq_9_last_evaluated") is not None
    assert hass.states.get("sensor.phq_9_score_interpretation") is not None


async def test_total_score_sensor_updates(hass: HomeAssistant) -> None:
    """Test that the total score sensor updates when the select entities change."""
    # Setup a mock person
    await async_setup_component(
        hass, "person", {"person": [{"name": "test", "id": "1234"}]}
    )
    hass.bus.async_fire(EVENT_HOMEASSISTANT_STARTED)
    await hass.async_block_till_done()

    entry = MockConfigEntry(domain=DOMAIN, data={})
    entry.add_to_hass(hass)

    with patch("asyncio.sleep", return_value=None):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.LOADED

    # Set the state of the select entities
    for i in range(9):
        hass.states.async_set(f"select.phq_9_question_{i+1}", "Several days")
        await hass.async_block_till_done()

    # Check that the total score sensor has updated
    assert hass.states.get("sensor.phq_9_total_score").state == "9"


async def test_score_interpretation_sensor_updates(hass: HomeAssistant) -> None:
    """Test that the score interpretation sensor updates when the total score sensor changes."""
    # Setup a mock person
    await async_setup_component(
        hass, "person", {"person": [{"name": "test", "id": "1234"}]}
    )
    hass.bus.async_fire(EVENT_HOMEASSISTANT_STARTED)
    await hass.async_block_till_done()

    entry = MockConfigEntry(domain=DOMAIN, data={})
    entry.add_to_hass(hass)

    with patch("asyncio.sleep", return_value=None):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.LOADED

    # Set the state of the total score sensor
    hass.states.async_set("sensor.phq_9_total_score", "15")
    await hass.async_block_till_done()

    # Check that the score interpretation sensor has updated
    assert (
        hass.states.get("sensor.phq_9_score_interpretation").state
        == "moderately_severe"
    )
