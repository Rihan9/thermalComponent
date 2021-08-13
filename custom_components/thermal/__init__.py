
from homeassistant.config_entries import SOURCE_REAUTH, ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers import entity_registry as er
from homeassistant.const import ATTR_FRIENDLY_NAME

import uuid, logging, asyncio

from .const import (
    DOMAIN,
    EVENT,
    EVENT_SENSORS,
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
# async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
#     entry.add_update_listener(options_update_listener)
#     p = Platform(hass, entry)
#     return await p.setup()
# 
# async def async_unload_entry(hass, entry):
#     _LOGGER.debug('unloading... %s ' % (entry.entry_id))
# 
#     # EntityRegistry = await er.async_get_registry(hass)
#     # EntityRegistry.async_clear_config_entry(entry.entry_id)
#     _LOGGER.debug('loaded integrations: %s' % hass.config.components)
#     await hass.config_entries.async_forward_entry_unload(entry, 'sensor')
#     await hass.config_entries.async_forward_entry_unload(entry, 'select')
#     if(DOMAIN in hass.data):
#         hass.data[DOMAIN].pop(entry.entry_id)
#     return True

async def options_update_listener(hass, entry):
    """Handle options update."""
    _LOGGER.debug('handle for config update. Data: %s, options: %s' % (entry.data, entry.options))

    if(entry.data.get('last_trigger_by') != entry.options.get('last_trigger_by') and entry.options.get('last_trigger_by') == 'update'):
        if(entry.options.get('operations') == 'delete'):
            sensor = list(filter(
                lambda d : d.get(ATTR_FRIENDLY_NAME) not in list(map(
                    lambda e : e.get(ATTR_FRIENDLY_NAME), 
                    entry.options.get(CONF_SENSORS)
                )), 
                entry.data.get(CONF_SENSORS)
            ))
            key_unique_id = sensor.get(ATTR_FRIENDLY_NAME).replace(' ', '_').lower() + '_id'
            entity_registry = await er.async_get_registry(hass)
            entity_id = entity_registry.async_get_entity_id('sensor', DOMAIN, entry.data.get(key_unique_id))
            entity_registry.async_remove(entity_id)
        hass.config_entries.async_update_entry(entry, data= {**entry.data, **{CONF_SENSORS: entry.options.get(CONF_SENSORS), 'last_trigger_by': 'update'}}, options={'operations':'none'})
    if(entry.data.get('last_trigger_by') != 'init'):
        await hass.config_entries.async_reload(entry.entry_id)
#     if(entry.options.get('operations') != 'none'):
#         if(entry.options.get('operations') == 'delete'):
# 
#             sensor = list(filter(
#                 lambda d : d.get(ATTR_FRIENDLY_NAME) not in list(map(
#                     lambda e : e.get(ATTR_FRIENDLY_NAME), 
#                     entry.options.get(CONF_SENSORS)
#                 )), 
#                 entry.data.get(CONF_SENSORS)
#             ))
#             key_unique_id = sensor.get(ATTR_FRIENDLY_NAME).replace(' ', '_').lower() + '_id'
#             entity_registry = await er.async_get_registry(hass)
#             entity_id = entity_registry.async_get_entity_id('sensor', DOMAIN, entry.data.get(key_unique_id))
#             entity_registry.async_remove(entity_id)
#         hass.config_entries.async_update_entry(entry, data= {**entry.data, **{CONF_SENSORS: entry.options.get(CONF_SENSORS), 'last_trigger_by': 'flow_option'}}, options={'operations':'none'})
#     elif(entry.data.get('last_trigger_by') == 'flow_option'):
#         await hass.config_entries.async_reload(entry.entry_id)
    # if(entry.options.get('FROM_CONFIGURE_FLOW')):
    #     await hass.config_entries.async_reload(entry.entry_id)
    
    return True