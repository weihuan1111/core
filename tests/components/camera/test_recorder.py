"""The tests for camera recorder."""
from __future__ import annotations

from datetime import timedelta

from homeassistant.components import camera
from homeassistant.components.recorder.models import StateAttributes, States
from homeassistant.components.recorder.util import session_scope
from homeassistant.core import State
from homeassistant.setup import async_setup_component
from homeassistant.util import dt as dt_util

from tests.common import async_fire_time_changed, async_init_recorder_component
from tests.components.recorder.common import async_wait_recording_done_without_instance


async def test_exclude_attributes(hass):
    """Test camera registered attributes to be excluded."""
    await async_init_recorder_component(hass)
    await async_setup_component(
        hass, camera.DOMAIN, {camera.DOMAIN: {"platform": "demo"}}
    )
    await hass.async_block_till_done()
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(minutes=5))
    await hass.async_block_till_done()
    await async_wait_recording_done_without_instance(hass)

    def _fetch_camera_states() -> list[State]:
        with session_scope(hass=hass) as session:
            native_states = []
            for db_state, db_state_attributes in session.query(States, StateAttributes):
                state = db_state.to_native()
                state.attributes = db_state_attributes.to_native()
                native_states.append(state)
            return native_states

    states: list[State] = await hass.async_add_executor_job(_fetch_camera_states)
    assert len(states) > 1
    for state in states:
        assert "access_token" not in state.attributes
        assert "entity_picture" not in state.attributes
        assert "friendly_name" in state.attributes
