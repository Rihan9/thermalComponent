import logging, uuid

from homeassistant.helpers.entity import async_generate_entity_id
from homeassistant.helpers.dispatcher import async_dispatcher_connect, async_dispatcher_send
from homeassistant.components.select import SelectEntity, ENTITY_ID_FORMAT 
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.core import (
    callback
)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers import entity_registry as er


from .const import CLOTHING_COEFICENT_VALUES, METHABOLIC_COEFICENT_VALUES, DOMAIN, EVENT, DATA_UPDATED, EVENT_SELECT_UPDATE


_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_devices):
    devices = []
    #data = dict(config_entry)
    entity_registry = await er.async_get_registry(hass)
    meth_id = config_entry.data.get('methabolic_id', str(uuid.uuid4()))
    cloth_id = config_entry.data.get('clothing_id', str(uuid.uuid4()))
    meth = entity_registry.async_get_entity_id('select', DOMAIN, meth_id)
    cloth = entity_registry.async_get_entity_id('select', DOMAIN, cloth_id)
    clothing_entity = Configurator(
        hass,
        'clothing',
        'clothing',
        'clothing',
        unique_id=cloth_id
    )
    devices.append(clothing_entity)
    methabolic_entity = Configurator(
        hass,
        'methabolic',
        'methabolic',
        'methabolic',
        unique_id=meth_id
    )
    devices.append(methabolic_entity)
    if(len(devices) > 0):
        async_add_devices(devices)
    # if('methabolic_id' not in config_entry.data):
    hass.config_entries.async_update_entry(config_entry, data={**config_entry.data, **{
        'last_trigger_by': 'init','clothing_id': cloth_id,'methabolic_id': meth_id}})

async def async_unload_entry(hass, entry):
    _LOGGER.debug('unload config_entry: ' + str(entry.data))
    return True

class Configurator(SelectEntity, RestoreEntity):
    def __init__(self, hass, device_id, name, entries_type, unique_id=str(uuid.uuid4())):
        self.hass = hass
        self._device_id = device_id
        # self.entity_id = async_generate_entity_id(ENTITY_ID_FORMAT, device_id, hass=hass)
        self._name = name
        self._entries_type = entries_type
        self._current_option = None# self.options[0]
        self._device_state_attributes = {}
        self._unique_id = unique_id
    
    @property
    def unique_id(self):
        return self._unique_id
    
    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name
    
    @property
    def options(self):
        if(self._entries_type == 'methabolic'):
            return list(METHABOLIC_COEFICENT_VALUES.keys())
        else:
            return  list(CLOTHING_COEFICENT_VALUES.keys())
    
    @property
    def current_option(self) -> str:
        """Return the selected entity option to represent the entity state."""
        return self._current_option
    
    def select_option(self, option: str):
        """Change the selected option."""
        self._current_option = option
        if(self._entries_type == 'methabolic'):
            self._device_state_attributes['value'] = METHABOLIC_COEFICENT_VALUES.get(self._current_option)
        else:
            self._device_state_attributes['value'] = CLOTHING_COEFICENT_VALUES.get(self._current_option)
        
        async_dispatcher_send(self.hass, EVENT_SELECT_UPDATE, {
            'key': self._entries_type,
            'value': self._device_state_attributes['value']
        })
    
    # async def async_update(self):
    #     return True
    @property
    def device_state_attributes(self):
        return self._device_state_attributes

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await super().async_added_to_hass()
        if self._current_option is not None:
            return
        state = await self.async_get_last_state()
        _LOGGER.debug('%s founded state: %s' % (self.entity_id, state) )
        if state is None or state.state not in self.options:
            self._current_option = self.options[0]
        else:
            self._current_option = state.state
        _LOGGER.debug('%s current_option: %s' % (self.entity_id, self._current_option) )
        if(self._entries_type == 'methabolic'):
            self._device_state_attributes['value'] = METHABOLIC_COEFICENT_VALUES.get(self._current_option)
        else:
            self._device_state_attributes['value'] = CLOTHING_COEFICENT_VALUES.get(self._current_option)
        # async_dispatcher_connect(
        #     self.hass, DATA_UPDATED, self._schedule_immediate_update
        # )
        # self.async_write_ha_state()
        self.async_schedule_update_ha_state(True)
    
    @callback
    def _schedule_immediate_update(self):
        self.async_schedule_update_ha_state(True)