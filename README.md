# hass-cozytouch
[![Sonarcloud Status](https://sonarcloud.io/api/project_badges/measure?project=biker91620_ha-cozytouch&metric=alert_status)](https://sonarcloud.io/dashboard?id=biker91620_ha-cozytouch)

Cozytouch support for Home Assistant

# Requirements
To get started:

    pip install git+https://github.com/biker91620/cozypy.git


## Cozytouch heaters switch component
#### Configuration variables:
**username** (Required):  Your user id (email)

**password** (Required): Your password

#### Example:
```
switch:
  - platform: cozytouch
    username: cozytouch@ilove.com
    password: cozytouch
```

## Cozytouch climat component
#### Configuration variables:
**username** (Required):  Your user id (email)

**password** (Required): Your password

#### Example:
```
climate:
  - platform: cozytouch
    username: cozytouch@ilove.com
    password: cozytouch
```


## Cozytouch temperature sensor component
#### Configuration variables:
**username** (Required):  Your user id (email)

**password** (Required): Your password

#### Example:
```
sensor:
  - platform: cozytouch
    username: cozytouch@ilove.com
    password: cozytouch
```


## Cozytouch occupancy sensor
#### Configuration variables:
**username** (Required):  Your user id (email)

**password** (Required): Your password

#### Example:
```
binary_sensor:
  - platform: cozytouch
    username: cozytouch@ilove.com
    password: cozytouch
```
