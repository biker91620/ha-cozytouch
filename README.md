# ha-cozytouch
Cozytouch support for Home Assistant

# Requirements
To get started:

    pip install git+https://github.com/biker91620/cozypy.git


## Cozytouch heaters switch component
#### Configuration variables:
**userId** (Required):  Your user id (email)

**userPassword** (Required): Your password

#### Example:
```
switch:
  - platform: cozytouch
    userId: cozytouch@ilove.com
    userPassword: cozytouch
```

## Cozytouch climat component
#### Configuration variables:
**userId** (Required):  Your user id (email)

**userPassword** (Required): Your password

#### Example:
```
climate:
  - platform: cozytouch
    userId: cozytouch@ilove.com
    userPassword: cozytouch
```


## Cozytouch temperature sensor component
#### Configuration variables:
**userId** (Required):  Your user id (email)

**userPassword** (Required): Your password

#### Example:
```
sensor:
  - platform: cozytouch
    userId: cozytouch@ilove.com
    userPassword: cozytouch
```


## Cozytouch occupancy sensor
#### Configuration variables:
**userId** (Required):  Your user id (email)

**userPassword** (Required): Your password

#### Example:
```
binary_sensor:
  - platform: cozytouch
    userId: cozytouch@ilove.com
    userPassword: cozytouch
```
