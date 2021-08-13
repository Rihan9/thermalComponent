
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

import logging

from .const import (
    CONF_SENSORS,
    
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    entry.add_update_listener(options_update_listener)
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(
            entry, "select"
        )
    )
    hass.async_create_task(           
        hass.config_entries.async_forward_entry_setup(
            entry, "sensor"
        )
    )
    return True

async def async_unload_entry(hass, entry):
    _LOGGER.debug('unloading... %s ' % (entry.entry_id))
    await hass.config_entries.async_forward_entry_unload(entry, 'sensor')
    await hass.config_entries.async_forward_entry_unload(entry, 'select')
    return True

async def options_update_listener(hass, entry):
    """Handle options update."""
    _LOGGER.debug('handle for config update. Data: %s, options: %s' % (entry.data, entry.options))

    if(entry.data.get('last_trigger_by') != entry.options.get('last_trigger_by') and entry.options.get('last_trigger_by') == 'update'):
        hass.config_entries.async_update_entry(entry, data= {**entry.data, **{CONF_SENSORS: entry.options.get(CONF_SENSORS), 'last_trigger_by': 'update'}}, options={'operations':'none'})
        hass.async_create_task(
            hass.config_entries.async_reload(entry.entry_id)
        )
    
    return True