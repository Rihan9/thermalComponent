import logging, json, math, uuid
from .utils import pmvEN, get_mean_radiant_temperature
import voluptuous as vol
from homeassistant.helpers.entity import Entity, async_generate_entity_id
from homeassistant.helpers import entity_registry as er
from homeassistant.components.sensor import SensorEntity, ENTITY_ID_FORMAT, PLATFORM_SCHEMA
from homeassistant.const import (ATTR_FRIENDLY_NAME, CONF_ICON_TEMPLATE, CONF_SENSORS, STATE_UNAVAILABLE, STATE_UNKNOWN)
from homeassistant.helpers.event import async_track_state_change
from homeassistant.helpers.dispatcher import async_dispatcher_send
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN, 
    EVENT_SENSORS,
    RELATIVE_AIR_SPEED, 
    CONF_WIND_SENSOR, 
    CONF_TYPE, 
    CONF_TEMPERATURE_SENSOR, 
    CONF_EXTERNAL_TEMPERATURE_SENSOR, 
    CONF_HUMIDITY_SENSOR, 
    CONF_METHABOLIC_ENTITY, 
    CONF_CLOTHING_ENTITY,
    CLOTHING_COEFICENT_VALUES,
    METHABOLIC_COEFICENT_VALUES,
#    EXTERNAL_WIND_FACTOR,
    CONF_MEAN_TEMPERATURE_SENSOR
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_devices):
    _LOGGER.debug('config_entry: ' + str(config_entry.data))# +json.dumps(config_entry.data))
    devices = []
    if(config_entry.data.get('clothing_id') != None and config_entry.data.get('methabolic_id') != None):
        entity_registry = await er.async_get_registry(hass)
        meth = entity_registry.async_get_entity_id('select', DOMAIN, config_entry.data.get('methabolic_id')) # c
        cloth = entity_registry.async_get_entity_id('select', DOMAIN, config_entry.data.get('clothing_id'))
    else:
        meth = 'select.methabolic'
        cloth = 'select.clothing'
    _LOGGER.debug('meth: %s, cloth: %s' % (meth, cloth))# +json.dumps(config_entry.data))
    sensor_data = {
        'unique_id': config_entry.entry_id
    }
    for sensor in config_entry.data.get('sensors'):
        s = PmvSensor(
            hass,
            sensor.get(ATTR_FRIENDLY_NAME).replace(' ', '_').lower(),
            sensor.get(CONF_TEMPERATURE_SENSOR),
            sensor.get(CONF_HUMIDITY_SENSOR),
            methabolic_entity=meth,
            clothing_entity=cloth,
            name=sensor.get(ATTR_FRIENDLY_NAME),
            sensor_type=sensor.get(CONF_TYPE),
            wind_sensor=sensor.get(CONF_WIND_SENSOR),
            unique_id=config_entry.data.get(sensor.get(ATTR_FRIENDLY_NAME).replace(' ', '_').lower() + '_id', str(uuid.uuid4()))
        )
        devices.append(s)
        sensor_data[sensor.get(ATTR_FRIENDLY_NAME).replace(' ', '_').lower() + '_id'] = s.unique_id
    _LOGGER.debug('number of sensors: %s' % len(devices))
    async_add_devices(devices)
    async_dispatcher_send(hass, EVENT_SENSORS, sensor_data)
    # return True

async def async_unload_entry(hass, entry):
    _LOGGER.debug('unload config_entry: ' + str(entry.data))# +json.dumps(config_entry.data))
    entity_registry = await er.async_get_registry(hass)
    for key_unique_id in list(filter(lambda i : i.endswith('_id') and i not in ['clothing_id', 'methabolic_id'], entry.data.keys())):
        _LOGGER.debug('entity_unique_id: %s' % entry.data.get(key_unique_id))
        entity_id = entity_registry.async_get_entity_id('sensor', DOMAIN, entry.data.get(key_unique_id))
        _LOGGER.debug('entity_id: %s' % entity_id)
        if(entity_id is not None):
            entity_registry.async_remove(entity_id)
    return True

def describe_state(state):
    if state < -0.7:
        return 'cold'
    if state > -0.7 and state <= -0.5:
        return 'CAT III: aceptable cool'
    elif state > -0.5 and state <= -0.2:
        return 'CAT II: confortable but slightly cool'
    elif state > -0.2 and state <= 0.2:
        return 'CAT I: confortable'
    elif state > 0.2 and state <= 0.5:
        return 'CAT II: confortable but slightly warm'
    elif state > 0.5 and state <= 0.7:
        return 'CAT III: aceptable warm'
    elif state > 0.7:
        return 'hot'
    else:
        return 'are you still alive?'


class PmvSensor(Entity):

    def __init__(self, 
        hass, 
        device_id, 
        temperature_sensor, 
        humidity_sensor, 
        wind_sensor=None, 
        methabolic_entity=None, 
        clothing_entity=None, 
        sensor_type='internal', 
        name='Thermal Comfort',
        unique_id=str(uuid.uuid4())):
        """Initialize the sensor."""
        self._state = 0
        self.hass = hass
        # self.entity_id = async_generate_entity_id(ENTITY_ID_FORMAT, device_id, hass=hass)
        self._sensor_type = sensor_type
        self._device_state_attributes = {}
        self._name = name
        self._device_id = device_id
        self._unique_id = unique_id
        self.handlers = []

        if(unique_id is None):
            raise Exception('how dare you!!')

        self.input_sensors = {
            'temperature': {
                'entity': temperature_sensor,
                'value': 0.00,
                'available': False
            },'humidity': {
                'entity': humidity_sensor,
                'value': 0.00,
                'available': False
            },'methabolic': {
                'entity': methabolic_entity,
                'value': 1.0 ,
                'available': methabolic_entity is None
            },'clothing': {
                'entity': clothing_entity,
                'value': 0.5 ,
                'available': clothing_entity is None
            },'wind': {
                'entity': wind_sensor,
                'value': RELATIVE_AIR_SPEED,
                'available': wind_sensor is None
            }
        }

        for entity_id in self.input_sensors:
            if(self.input_sensors[entity_id]['entity'] is None):
                continue
            self.states_listener(
                self.input_sensors[entity_id]['entity'],
                None,
                hass.states.get(self.input_sensors[entity_id]['entity'])
            )
            self.handlers.append(
                async_track_state_change(self.hass, self.input_sensors[entity_id]['entity'], self.states_listener)
            )

    async def async_will_remove_from_hass(self):
        _LOGGER.debug('%s removed from ha' % self.name)
        for handler in self.handlers:
            handler()
    
    @property
    def unique_id(self):
        if(self._unique_id is None):
            raise Exception('how dare you!!')
        return self._unique_id

    @property
    def available(self):
        available = True
        for entity_id in self.input_sensors:
            if(not self.input_sensors[entity_id]['available']):
                _LOGGER.debug('entity %s is unavailable' % (entity_id))
            available = available and self.input_sensors[entity_id]['available']
        return available

    def states_listener(self, entity, old_state, new_state):
        if(new_state == None or new_state.state == STATE_UNKNOWN or new_state.state == STATE_UNAVAILABLE):
            _LOGGER.debug('no state for entity %s' % (entity))
            return

        for entity_id in self.input_sensors:
            if(self.input_sensors[entity_id]['entity'] == entity):
                if(entity_id == 'methabolic'):
                    self.input_sensors[entity_id]['value'] = float(METHABOLIC_COEFICENT_VALUES.get(new_state.state))
                elif(entity_id == 'clothing'):
                    self.input_sensors[entity_id]['value'] = float(CLOTHING_COEFICENT_VALUES.get(new_state.state))
                else:
                    self.input_sensors[entity_id]['value'] = float(new_state.state)
                self.input_sensors[entity_id]['available'] = True
        if(self.entity_id is not None):
            self.async_schedule_update_ha_state(True)

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
    @property
    def device_state_attributes(self):
        return self._device_state_attributes
    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return 'i'

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    async def async_update(self):
        if(self.available):
            self._state = round(
                pmvEN(
                    self.input_sensors['temperature']['value'], # dry bulb air temperature
                    self.input_sensors['temperature']['value'], # mean radiant temperature
                    self.input_sensors['wind']['value'], # average air speed
                    self.input_sensors['humidity']['value'], # relative humidity
                    self.input_sensors['methabolic']['value'], # metabolic rate 
                    self.input_sensors['clothing']['value'], # clothing insulation
                    0)['pmv']
                , 2
            )

            t = self._state
            suggested_air_temp = int(round(self.input_sensors['temperature']['value'], 0))
            tentative = 11
            while abs(t) > 0.2 and tentative != 0:
                suggested_air_temp = suggested_air_temp + ( 1 if t < 0 else -1)
                tentative -= 1
                t = round(
                    pmvEN(
                        suggested_air_temp, # dry bulb air temperature
                        suggested_air_temp, # mean radiant temperature
                        self.input_sensors['wind']['value'], # average air speed
                        self.input_sensors['humidity']['value'], # relative humidity
                        self.input_sensors['methabolic']['value'], # metabolic rate 
                        self.input_sensors['clothing']['value'], # clothing insulation
                        0)['pmv']
                    , 2
                )
                _LOGGER.debug('try with %s, tentative left: %s, result: %s' % (suggested_air_temp, tentative, t))
            self._device_state_attributes['description'] = describe_state(self._state)
            self._device_state_attributes['air temperature'] = self.input_sensors['temperature']['value']
            self._device_state_attributes['suggested temperature'] = suggested_air_temp
            self._device_state_attributes['suggested HVAC'] = self.hvac(self.input_sensors['temperature']['value'], suggested_air_temp, self.input_sensors['humidity']['value'])
            self._device_state_attributes['mean radiant temperature'] = self.input_sensors['temperature']['value']
            self._device_state_attributes['air speed'] = self.input_sensors['wind']['value']
            self._device_state_attributes['humidity'] = self.input_sensors['humidity']['value']
            self._device_state_attributes['methabolic'] = self.input_sensors['methabolic']['value']
            self._device_state_attributes['clothing'] = self.input_sensors['clothing']['value']
    
    def hvac(self, temperature, target_temperature, humidity):
        if(humidity > 70):
            return 'dry'
        hvac = 'heat' if target_temperature > temperature else 'cool'
        if(target_temperature == int(round(temperature, 0))):
            hvac = 'off'
        if(hvac == 'cool' and humidity > 60):
            return 'dry'
        return hvac