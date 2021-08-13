import voluptuous as vol
import uuid, logging

from homeassistant.core import callback

from .const import (
    DOMAIN,
    CONF_TEMPERATURE_SENSOR,
    CONF_HUMIDITY_SENSOR,
    CONF_TYPE,
    CONF_WIND_SENSOR,
    CONF_SENSORS
)

from homeassistant import config_entries
from homeassistant.const import ATTR_FRIENDLY_NAME

TYPE_SCHEMA = vol.Schema({
    vol.Required(ATTR_FRIENDLY_NAME): str,
    vol.Required(CONF_TYPE): vol.In(["internal", "external"])
})
INTERNAL_SCHEMA = vol.Schema({
    vol.Required(CONF_TEMPERATURE_SENSOR): str,
    vol.Required(CONF_HUMIDITY_SENSOR): str,
    vol.Optional('addMoreSensor'): bool
})
EXTERNAL_SCHEMA = vol.Schema({
    vol.Required(CONF_TEMPERATURE_SENSOR): str,
    vol.Required(CONF_HUMIDITY_SENSOR): str,
    vol.Required(CONF_WIND_SENSOR): str,
    vol.Optional('addMoreSensor'): bool
})

INIT_OPTION_SCHEMA = vol.Schema({
    vol.Required(CONF_TYPE): vol.In(["update", "add", "delete"])
})



_LOGGER = logging.getLogger(__name__)
        
class ThermalComfortConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler(config_entry)
    
    async def async_step_user(self, info):
        if info is None:
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()
            self.sensors = []
            self.currentSensor = None
            return self._entity_form()
        elif(self.currentSensor == None):
            self.currentSensor = {
                CONF_TYPE: info.get(CONF_TYPE),
                ATTR_FRIENDLY_NAME: info.get(ATTR_FRIENDLY_NAME)
            }
            return self._entity_form(info.get(CONF_TYPE))
        else:
            self.currentSensor = {**self.currentSensor, **{
                CONF_TEMPERATURE_SENSOR: info.get(CONF_TEMPERATURE_SENSOR),
                CONF_HUMIDITY_SENSOR: info.get(CONF_HUMIDITY_SENSOR),
                CONF_WIND_SENSOR: info.get(CONF_WIND_SENSOR),
                CONF_WIND_SENSOR: info.get(CONF_WIND_SENSOR)
            }}
            self.sensors.append(self.currentSensor)
            self.currentSensor = None

            if(info.get('addMoreSensor', False)):
                return self._entity_form()
            else:
                return self.async_create_entry(
                    title='Thermal Comfort Platform',
                    data={
                        'last_trigger_by': 'init',
                        CONF_SENSORS: self.sensors,
                        'unique_id': str(uuid.uuid4())
                    }
                )

    def _entity_form(self, fType=None):
        if(fType is None):
            return self.async_show_form(
                step_id="user", data_schema=TYPE_SCHEMA
            )
        elif(fType == 'internal'):
            return self.async_show_form(
                step_id="user", data_schema=INTERNAL_SCHEMA
            )
        elif(fType == 'external'):
            return self.async_show_form(
                step_id="user", data_schema=EXTERNAL_SCHEMA
            )
        else:
            return self.async_abort(reason="unaxpected_behavior")

class OptionsFlowHandler(config_entries.OptionsFlow):

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry
        self._operation = None
        self.sensors = self.config_entry.data.get(CONF_SENSORS)
        self.currentSensor = None


    def remove_from_sensors(self, entity_name):
        sensors = list(filter(
            lambda a: a.get(ATTR_FRIENDLY_NAME) != entity_name, 
            self.sensors
        ))
        return sensors
    
    def update_to_sensors(self, sensor):
        sensors = self.remove_from_sensors(sensor.get(ATTR_FRIENDLY_NAME))
        sensors.append(sensor)
        return sensors

    
    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is None:
            return self.async_show_form(
                step_id="init",
                data_schema=INIT_OPTION_SCHEMA
            )
        if(CONF_TYPE in user_input and self._operation is None):
            self._operation = user_input.get(CONF_TYPE)
            if(self._operation in ['update', 'delete']):
                sensors = list(map(lambda a: a.get(ATTR_FRIENDLY_NAME), self.sensors))
                return self.async_show_form(
                    step_id="init",
                    data_schema=vol.Schema({
                        vol.Required(CONF_SENSORS): vol.In(sensors)
                    })
                )
            elif(self._operation == 'add'):
                return self.async_show_form(
                    step_id="user",
                    data_schema=TYPE_SCHEMA
                )
        if(CONF_SENSORS in user_input and self._operation == 'update'):
            self.currentSensor = list(filter(lambda a: a.get(ATTR_FRIENDLY_NAME) == user_input.get(CONF_SENSORS), self.sensors))[0]
            schema = vol.Schema({
                vol.Required(CONF_TEMPERATURE_SENSOR, default=self.currentSensor.get(CONF_TEMPERATURE_SENSOR)): str,
                vol.Required(CONF_HUMIDITY_SENSOR, default=self.currentSensor.get(CONF_HUMIDITY_SENSOR)): str
            })
            if(self.currentSensor.get(CONF_TYPE) == 'external'):
                schema = schema.extend({
                    vol.Required(CONF_WIND_SENSOR, default=self.currentSensor.get(CONF_WIND_SENSOR)): str
                })
            return self.async_show_form(
                step_id="init",
                data_schema=schema
            )
        if(CONF_SENSORS in user_input and self._operation == 'delete'):
            # self.sensors = list(filter(
            #     lambda a: a.get(ATTR_FRIENDLY_NAME) != user_input.get(CONF_SENSORS, {}).get(ATTR_FRIENDLY_NAME), 
            #     self.sensors
            # ))
            return self.async_create_entry(
                title='',
                data={
                    'last_trigger_by': 'update',
                    'operations': self._operation,
                    CONF_SENSORS: self.remove_from_sensors(user_input.get(CONF_SENSORS))
                }
            )
        if(CONF_SENSORS not in user_input and self._operation == 'update'):
            _LOGGER.debug('currentSensor: %s, user_input: %s' % (self.currentSensor, user_input))
            self.currentSensor = {**self.currentSensor, **user_input}
            _LOGGER.debug('updatedcurrentSensor: %s' % (self.currentSensor))
            # self.sensors = list(filter(lambda a: a.get(ATTR_FRIENDLY_NAME) != user_input.get(CONF_SENSORS, {}).get(ATTR_FRIENDLY_NAME), self.sensors))
            # self.sensors.append(self.currentSensor)

            _LOGGER.debug('sensors: %s' % (self.sensors))
            return self.async_create_entry(
                title='',
                data={
                    'last_trigger_by': 'update',
                    'operations': self._operation,
                    CONF_SENSORS: self.update_to_sensors(self.currentSensor)
                }
            )
        
    
    async def async_step_user(self, info):
        if(self.currentSensor == None):
            self.currentSensor = {
                CONF_TYPE: info.get(CONF_TYPE),
                ATTR_FRIENDLY_NAME: info.get(ATTR_FRIENDLY_NAME)
            }
            return self._entity_form(info.get(CONF_TYPE))
        else:
            self.currentSensor = {**self.currentSensor, **{
                CONF_TEMPERATURE_SENSOR: info.get(CONF_TEMPERATURE_SENSOR),
                CONF_HUMIDITY_SENSOR: info.get(CONF_HUMIDITY_SENSOR),
                CONF_WIND_SENSOR: info.get(CONF_WIND_SENSOR),
                CONF_WIND_SENSOR: info.get(CONF_WIND_SENSOR)
            }}
            self.sensors.append(self.currentSensor)
            self.currentSensor = None

            if(info.get('addMoreSensor', False)):
                return self._entity_form()
            else:
                return self.async_create_entry(
                    title='',
                    data={
                        'last_trigger_by': 'update',
                        'operations': self._operation,
                        CONF_SENSORS: self.sensors
                    }
                )

    def _entity_form(self, fType=None):
        if(fType is None):
            return self.async_show_form(
                step_id="user", data_schema=TYPE_SCHEMA
            )
        elif(fType == 'internal'):
            return self.async_show_form(
                step_id="user", data_schema=INTERNAL_SCHEMA
            )
        elif(fType == 'external'):
            return self.async_show_form(
                step_id="user", data_schema=EXTERNAL_SCHEMA
            )
        else:
            return self.async_abort(reason="unaxpected_behavior")