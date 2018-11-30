# ha-cozytouch
Cozytouch support for Home Assistant

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
