DOMAIN = 'thermal'
DATA_UPDATED = f"{DOMAIN}_data_updated"
# weight to calc mean value
T_INT_WEIGHT = 0.9
T_EXT_WEIGHT = 2 - T_INT_WEIGHT
INTERNAL_SUN_ELEVATION_FACTOR = 0.2
EXTERNAL_SUN_ELEVATION_FACTOR = 0.1
# EXTERNAL_WIND_FACTOR = 0.4

RELATIVE_AIR_SPEED = 0.1

CONF_TEMPERATURE_SENSOR = 'temperature_sensor'
CONF_HUMIDITY_SENSOR = 'humidity_sensor'
CONF_WIND_SENSOR = 'wind_sensor'
CONF_TYPE = 'type'
CONF_SENSORS = 'sensors'

EVENT = f"{DOMAIN}_selects_setup_complete"
EVENT_SELECT_UPDATE = f"{DOMAIN}_selects_update"
EVENT_SENSORS = f"{DOMAIN}_sensors_setup_complete"

CONF_INTERNAL_TEMPERATURE_SENSOR = 'internal_temperature_sensor'
CONF_EXTERNAL_TEMPERATURE_SENSOR = 'external_temperature_sensor'
CONF_MEAN_TEMPERATURE_SENSOR = 'mean_temperature_sensor'
CONF_METHABOLIC_ENTITY = 'methabolic_entry'
CONF_CLOTHING_ENTITY = 'clothing_entry'

METHABOLIC_COEFICENT_VALUES = {
    'Sleeping': 0.7,
    'Reclining': 0.8,
    'Seated, quiet': 1.0,
    'Reading, seated': 1.0,
    'Writing': 1.0,
    'Typing': 1.1,
    'Standing, relaxed': 1.2,
    'Filing, seated': 1.2,
    'Flying aircraft, routine': 1.2,
    'Filing, standing': 1.4,
    'Driving a car': 1.5,
    'Walking about': 1.7,
    'Cooking': 1.8,
    'Table sawing': 1.8,
    'Walking 2mph (3.2kmh)': 2.0,
    'Lifting/packing': 2.1,
    'Seated, heavy limb movement': 2.2,
    'Light machine work': 2.2,
    'Flying aircraft, combat': 2.4,
    'Walking 3mph (4.8kmh)': 2.6,
    'House cleaning': 2.7,
    'Driving, heavy vehicle': 3.2,
    'Dancing': 3.4,
    'Calisthenics': 3.5,
    'Walking 4mph (6.4kmh)': 3.8,
    'Tennis': 3.8,
    'Heavy machine work': 4.0,
    'Handling 100lb (45 kg) bags': 4.0,
    'Pick and shovel work': 4.4,
    'Basketball': 6.3,
    'Wrestling': 7.8
}

CLOTHING_COEFICENT_VALUES = {
    'Like mom made you': 0.25,
    'Only underwear': 0.30,
    'Walking shorts, short-sleeve shirt': 0.36,
    'Typical summer indoor clothing': 0.5,
    'Knee-length skirt, short-sleeve shirt, sandals, underwear': 0.54,
    'Trousers, short-sleeve shirt, socks, shoes, underwear': 0.57,
    'Trousers, long-sleeve shirt': 0.61,
    'Knee-length skirt, long-sleeve shirt, full slip': 0.67,
    'Sweat pants, long-sleeve sweatshirt': 0.74,
    'Jacket, Trousers, long-sleeve shirt': 0.96,
    'Typical winter indoor clothing': 1.0
}