
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
    p = Platform(hass, entry)
    return await p.setup()

async def async_unload_entry(hass, entry):
    _LOGGER.debug('unloading... %s ' % (entry.entry_id))

    # EntityRegistry = await er.async_get_registry(hass)
    # EntityRegistry.async_clear_config_entry(entry.entry_id)
    _LOGGER.debug('loaded integrations: %s' % hass.config.components)
    await hass.config_entries.async_forward_entry_unload(entry, 'sensor')
    await hass.config_entries.async_forward_entry_unload(entry, 'select')
    if(DOMAIN in hass.data):
        hass.data[DOMAIN].pop(entry.entry_id)
    return True

async def options_update_listener(hass, entry):
    """Handle options update."""
    _LOGGER.debug('handle for config update. Data: %s, options: %s' % (entry.data, entry.options))
    if(entry.options.get('operations') != 'none'):
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
        hass.config_entries.async_update_entry(entry, data= {**entry.data, **{CONF_SENSORS: entry.options.get(CONF_SENSORS)}}, options={'operations':'none'})
        await hass.config_entries.async_reload(entry.entry_id)
    # if(entry.options.get('FROM_CONFIGURE_FLOW')):
    #     await hass.config_entries.async_reload(entry.entry_id)
    
    return True

class Platform():
    def __init__(self, hass, entry):
        self.hass = hass
        self.entry = entry 
        self.select_done = False
        self.sensor_done = False
    
    async def setup(self):
        async_dispatcher_connect(
            self.hass, EVENT, self._create_picklist_callback
        )
        async_dispatcher_connect(
            self.hass, EVENT_SENSORS, self._create_sensors_callback
        )
        # self.hass.async_listen(EVENT, self._create_picklist_callback)
        self.hass.async_create_task(
            self.hass.config_entries.async_forward_entry_setup(
                self.entry, "select"
            )
        )
        i = 10
        while i > 0 and (not self.select_done or not self.sensor_done):
            await asyncio.sleep(2)
            i -= 1
        return True
    @callback
    def _create_picklist_callback(self, data):
        self.select_done = True
        if(self.entry.entry_id != data.get('unique_id')):
            _LOGGER.debug('incoming event from other integration (%s --> %s). abort' %(self.entry.entry_id, data.get('unique_id')))
            return
        self.hass.config_entries.async_update_entry(self.entry, data={**self.entry.data , **{
            'clothing_id': data.get('clothing_id'),
            'methabolic_id': data.get('methabolic_id')
        }})
        self.hass.async_create_task(
            self.hass.config_entries.async_forward_entry_setup(
                self.entry, "sensor"
            )
        )
    @callback
    def _create_sensors_callback(self, data):
        self.sensor_done = True
        self.hass.config_entries.async_update_entry(self.entry, data={**self.entry.data , **data})