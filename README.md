# Cozytouch
This a *custom component* for [Home Assistant](https://www.home-assistant.io/). 
[![Sonarcloud Status](https://sonarcloud.io/api/project_badges/measure?project=biker91620_ha-cozytouch&metric=alert_status)](https://sonarcloud.io/dashboard?id=biker91620_ha-cozytouch)

There is currently support for the following device types within Home Assistant:

* [Sensor](#sensor) with temperature, occupancy, electricalpower metrics, ...
* [Climate sensor](#sensor) with preset mode
* [Water Heater sensor](#presence-detection) with hvac mode , boost mode , wway


![GitHub release](https://img.shields.io/github/release/Cyr-ius/hass-cozytouch)
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)



## Configuration

The preferred way to setup the platform is by enabling the discovery component.
Add your equipment via the Integration menu

Otherwise, you can set it up manually in your `configuration.yaml` file:

```yaml
cozytouch:
  username: cozytouch@ilove.com
  password: cozytouch
```
