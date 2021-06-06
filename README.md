# Cozytouch
This a *custom component* for [Home Assistant](https://www.home-assistant.io/). 

With COZYTOUCH, you control your thermal comfort solutions (heating, air conditioning, etc.) from where you want and when you want.

There is currently support for the following device types within Home Assistant:

* [Sensor](#sensor) with temperature, occupancy, electricalpower metrics, ...
* [Climate sensor](#sensor) with preset mode
* [Water Heater sensor](#presence-detection) with hvac mode , boost mode , away


![GitHub release](https://img.shields.io/github/release/Cyr-ius/hass-cozytouch)
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)

## Configuration

The preferred way to setup the platform is by enabling the discovery component.
Add your equipment via the Integration menu

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=cozytouch)
