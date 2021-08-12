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


from .const import CLOTHING_COEFICENT_VALUES, METHABOLIC_COEFICENT_VALUES, DOMAIN, EVENT, DATA_UPDATED


_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_devices):
    devices = []
    #data = dict(config_entry)
    clothing_entity = Configurator(
        hass,
        'clothing',
        'clothing',
        'clothing',
        unique_id=config_entry.data.get('clothing_id', str(uuid.uuid4()))
    )
    methabolic_entity = Configurator(
        hass,
        'methabolic',
        'methabolic',
        'methabolic',
        unique_id=config_entry.data.get('methabolic_id', str(uuid.uuid4()))
    )
    devices.append(clothing_entity)
    devices.append(methabolic_entity)
    async_add_devices(devices)
    async_dispatcher_send(hass, EVENT, {
        'unique_id': config_entry.entry_id,
        'clothing_id': clothing_entity.unique_id,
        'methabolic_id': methabolic_entity.unique_id
    })
    # await hass.bus.async_fire(EVENT, {
    #     'unique_id': config_entry.entry_id,
    #     'clothing': clothing_entity.entity_id,
    #     'methabolic': methabolic_entity.entity_id
    # })
    # return True

async def async_unload_entry(hass, entry):
    _LOGGER.debug('unload config_entry: ' + str(entry.data))# +json.dumps(config_entry.data))
    entity_registry = await er.async_get_registry(hass)
    for key_unique_id in list(filter(lambda i : i.endswith('_id') and i in ['clothing_id', 'methabolic_id'], entry.data.keys())):
        _LOGGER.debug('entity_unique_id: %s' % entry.data.get(key_unique_id))
        entity_id = entity_registry.async_get_entity_id('select', DOMAIN, entry.data.get(key_unique_id))
        _LOGGER.debug('entity_id: %s' % entity_id)
        if(entity_id is not None):
            entity_registry.async_remove(entity_id)
    return True

class Configurator(SelectEntity, RestoreEntity):
    def __init__(self, hass, device_id, name, entries_type, unique_id=str(uuid.uuid4())):
        self.hass = hass
        self._device_id = device_id
        self.entity_id = async_generate_entity_id(ENTITY_ID_FORMAT, device_id, hass=hass)
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