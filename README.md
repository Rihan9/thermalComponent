# Eufy Security Integrations for Home Assistant

## Installation

### Install from HACS:

- Add this repository (https://github.com/Rihan9/thermalComponent) on your hacs installation (Category: Integration) and search for "Thermal Comfort" integration.
- After restart of home assistant go in setup -> Integration -> Add -> "Thermal Comfort".
- There are 2 main screen on setup:
    - the first screen is used to set the name of the sensor end the type. It can be internal or external. The only difference is that a wind sensor is required in the external   sensor 
    - the second screen is used to set the sensors used on calculation. You can add multiple sensors directly on first setup, selecting the "add more" checkbox.

The configure flow can be used to add more sensors later, update or remove existing sensors.


## KNOW ISSUES:

- [ ] the first state of select is not sended to sensor if the select is loaded first
- [ ] the delete operation not work: cannot find correct sensor on flow to remove
- [ ] the update operation not work: create a new sensor with the same reference causing errors
- [X] the reload and delete flow for config entry does not seem to work properly. It needs to be fixed before first release : FIXED

