import requests
from requests.exceptions import HTTPError
import pickle
import time
import logging
import json
import yaml
from pathlib import Path

import lupulib.devices.alarm as ALARM
import lupulib.constants as CONST
from lupulib.devices.binary_sensor import LupusecBinarySensor
from lupulib.devices.switch import LupusecSwitch

_LOGGER = logging.getLogger(__name__)
home = str(Path.home())


class Lupusec:
    """Interface to Lupusec Webservices."""

    def __init__(self, username, password, ip_address, get_devices=False):
        """LupsecAPI constructor requires IP and credentials to the
        Lupusec Webinterface.
        """
        # _LOGGER.debug("Lupusec.__init__ started...")
        # _LOGGER.debug('Init LupusecSystem: %s, %s, %s, %s',
        #    name, ip_address, username, password)
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.api_url = "http://{}/action/".format(ip_address)
        self.model = "unknown"
        self.headers = None
        response = self._request_get("tokenGet")
        _LOGGER.debug('HTTP-Responde-Code: %s', response.status_code)

        if response.status_code == 404:
            resp = self.session.get(CONST.DEVICES_API_XT1)
            if resp.status_code == 200:
                _LOGGER.debug("XT1 found, setting it up")
                self.model = 1
                self.mode_translation = CONST.MODE_TRANSLATION_XT1
                self.api_mode = "mode_st"
                self.api_sensors = CONST.DEVICES_API_XT1
                self.api_device_id = "no"
                self._request_post("login")
            else:
                _LOGGER.debug("Unknown error while finding out which model is used")
                return
        else:
            _LOGGER.debug("XT2 or higher found, setting up")
            self.model = 2
            self.mode_translation = CONST.MODE_TRANSLATION_XT2
            self.api_mode = "mode_a1"
            self.api_sensors = CONST.DEVICES_API_XT2
            self.api_device_id = "sid"
            self.headers = {"X-Token": json.loads(response.text)["message"]}
        self._mode = None
        self._devices = None

        try:
            self._history_cache = pickle.load(
                open(home + "/" + CONST.HISTORY_CACHE_NAME, "rb")
            )
        except (OSError, IOError) as e:
            self._history_cache = []
            pickle.dump(
                self._history_cache, open(home + "/" + CONST.HISTORY_CACHE_NAME, "wb")
            )

        self._panel = self.get_panel()
        _LOGGER.debug("self.get_panel()...")
        self._cacheSensors = None
        self._cacheStampS = time.time()
        self._cachePss = None
        self._cacheStampP = time.time()

        #if get_devices or self._devices is None:
         #   _LOGGER.debug("self.get_devices()...")
         #   self.get_devices()

    def _request_get(self, action):
        response = self.session.get(
            self.api_url + action, timeout=15, headers=self.headers
        )
        _LOGGER.debug(
            "Action and statuscode of apiGET command: %s, %s",
            action,
            response.status_code,
        )
        return response

    def _request_post(self, action, params={}):
        return self.session.post(
            self.api_url + action, data=params, headers=self.headers
        )

    def clean_json(self, textdata):
        _LOGGER.debug("clean_json(): " + textdata)
        if self.model == 1:
            textdata = textdata.replace("\t", "")
            i = textdata.index("\n")
            textdata = textdata[i + 1 : -2]
            try:
                textdata = yaml.load(textdata, Loader=yaml.BaseLoader)
            except Exception as e:
                _LOGGER.warning(
                    "lupulib couldn't parse provided response: %s, %s", e, textdata
                )
            return textdata
        else:
            return json.loads(textdata, strict=False)

    def get_power_switches(self):
        _LOGGER.debug("get_power_switches() called:")
        stampNow = time.time()
        length = len(self._devices)
        if self._cachePss is None or stampNow - self._cacheStampP > 2.0:
            self._cacheStamp_p = stampNow
            response = self._request_get("pssStatusGet")
            response = self.clean_json(response.text)["forms"]
            powerSwitches = []
            counter = 1
            for pss in response:
                powerSwitch = {}
                if response[pss]["ready"] == 1:
                    powerSwitch["status"] = response[pss]["pssonoff"]
                    powerSwitch["device_id"] = counter + length
                    powerSwitch["type"] = CONST.TYPE_POWER_SWITCH
                    powerSwitch["name"] = response[pss]["name"]
                    powerSwitches.append(powerSwitch)
                else:
                    _LOGGER.debug("Pss skipped, not active")
                counter += 1
            self._cachePss = powerSwitches

        return self._cachePss

    def get_sensors(self):
        _LOGGER.debug("get_sensors() called:")
        stamp_now = time.time()
        if self._cacheSensors is None or stamp_now - self._cacheStampS > 2.0:
            self._cacheStampS = stamp_now
            response = self._request_get(self.api_sensors)
            response = self.clean_json(response.text)["senrows"]
            sensors = []
            for device in response:
                device["status"] = device["cond"]
                device["device_id"] = device[self.api_device_id]
                device.pop("cond")
                device.pop(self.api_device_id)
                if not device["status"]:
                    device["status"] = "Geschlossen"
                else:
                    device["status"] = None
                sensors.append(device)
            self._cacheSensors = sensors

        return self._cacheSensors

    def get_panel(self):
        _LOGGER.debug("get_panel() called:")
	# we are trimming the json from Lupusec heavily, since its bullcrap
        response = self._request_get("panelCondGet")
        if response.status_code != 200:
            raise Exception("Unable to get panel " + response.status_code)
        panel = self.clean_json(response.text)["updates"]
        panel["mode"] = panel[self.api_mode]
        panel.pop(self.api_mode)

        if self.model == 2:
            panel["mode"] = CONST.XT2_MODES_TO_TEXT[panel["mode"]]
        panel["device_id"] = CONST.ALARM_DEVICE_ID
        panel["type"] = CONST.ALARM_TYPE
        panel["name"] = CONST.ALARM_NAME

        # history = self.get_history()

        if self.model == 1:
            for histrow in history:
                if histrow not in self._history_cache:
                    if (
                        CONST.MODE_ALARM_TRIGGERED
                        in histrow[CONST.HISTORY_ALARM_COLUMN]
                    ):
                        panel["mode"] = CONST.STATE_ALARM_TRIGGERED
                    self._history_cache.append(histrow)
                    pickle.dump(
                        self._history_cache,
                        open(home + "/" + CONST.HISTORY_CACHE_NAME, "wb"),
                    )
        elif self.model == 2:
            _LOGGER.debug("Alarm on XT2 not implemented")
        return panel

    def get_history(self):
        _LOGGER.debug("get_history() called: ")
        response = self._request_get(CONST.HISTORY_REQUEST)
        return self.clean_json(response.text)[CONST.HISTORY_HEADER]

    def refresh(self):
        _LOGGER.debug("refresh() called: ")
        """Do a full refresh of all devices and automations."""
        self.get_devices(refresh=True)

    def get_devices(self, refresh=False, generic_type=None):
        _LOGGER.debug("get_devices() called: ")
        """Get all devices from Lupusec."""
        _LOGGER.info("Updating all devices...")
        if refresh or self._devices is None:
            if self._devices is None:
                self._devices = {}

            responseObject = self.get_sensors()
            if responseObject and not isinstance(responseObject, (tuple, list)):
                responseObject = responseObject

            _LOGGER.debug("...iterate over all devices on responseObject:")
            for deviceJson in responseObject:
                # Attempt to reuse an existing device
                device = self._devices.get(deviceJson["name"])
                _LOGGER.debug("...device: " + deviceJson["name"])
                # No existing device, create a new one
                if device:
                    _LOGGER.debug("...update existing device: " + deviceJson["name"])
                    device.update(deviceJson)
                else:
                    _LOGGER.debug("...newDevice found: " + deviceJson["name"])
                    device = self.newDevice(deviceJson, self)

                    if not device:
                        _LOGGER.info("Device is unknown")
                        continue

                    self._devices[device.device_id] = device

            # We will be treating the Lupusec panel itself as an armable device.
            panelJson = self.get_panel()
            _LOGGER.debug("Get the panel in get_devices: %s", panelJson)

            self._panel.update(panelJson)

            alarmDevice = self._devices.get("0")

            if alarmDevice:
                alarmDevice.update(panelJson)
            else:
                alarmDevice = ALARM.create_alarm(panelJson, self)
                self._devices["0"] = alarmDevice

            # Now we will handle the power switches
            if self.model == 1:
                switches = self.get_power_switches()
                _LOGGER.debug("Get active the power switches in get_devices: %s", switches)

                for deviceJson in switches:
                    # Attempt to reuse an existing device
                    device = self._devices.get(deviceJson["name"])

                    # No existing device, create a new one
                    if device:
                        device.update(deviceJson)
                    else:
                        device = self.newDevice(deviceJson, self)
                        if not device:
                            _LOGGER.info("Device is unknown")
                            continue
                        self._devices[device.device_id] = device

            elif self.model == 2:
                _LOGGER.debug("Power switches for XT2 not implemented")

        if generic_type:
            devices = []
            for device in self._devices.values():
                if device.type is not None and device.type in generic_type[0]:
                    devices.append(device)
            return devices

        return list(self._devices.values())

    def get_device(self, device_id, refresh=False):
        """Get a single device."""
        _LOGGER.debug("get_device() called for single device: ")
        if self._devices is None:
            self.get_devices()
            refresh = False

        device = self._devices.get(device_id)

        if device and refresh:
            device.refresh()

        return device

    def get_alarm(self, area="1", refresh=False):
        """Shortcut method to get the alarm device."""
        _LOGGER.debug("get_alarm() called: ")
        if self._devices is None:
            self.get_devices()
            refresh = False

        return self.get_device(CONST.ALARM_DEVICE_ID, refresh)


    def get_info(self):
        """Shortcut method to get the system info."""
        _LOGGER.debug("get_info() called: ")

        response = self._request_get(CONST.INFO_REQUEST)
        json_response = response.json()
        _LOGGER.debug(json_response)
        json_data = json_response["updates"]
        _LOGGER.debug("  Hardware-Version: %s ", json_data["rf_ver"])
        _LOGGER.debug("  Firmware-Version: %s ", json_data["em_ver"])

        return self.clean_json(response.text)[CONST.INFO_HEADER]


    def set_mode(self, mode):
        if self.model == 1:
            params = {
                "mode": mode,
            }
        elif self.model == 2:
            params = {"mode": mode, "area": 1}
        r = self._request_post("panelCondPost", params)
        responseJson = self.clean_json(r.text)
        return responseJson


def newDevice(deviceJson, lupusec):
    """Create new device object for the given type."""
    _LOGGER.debug("newDevice() called: name=" + deviceJson["name"])
    type_tag = deviceJson.get("type")

    if not type_tag:
        _LOGGER.info("Device has no type")

    if type_tag in CONST.TYPE_OPENING:
        return LupusecBinarySensor(deviceJson, lupusec)
    elif type_tag in CONST.TYPE_SENSOR:
        return LupusecBinarySensor(deviceJson, lupusec)
    elif type_tag in CONST.TYPE_SWITCH:
        return LupusecSwitch(deviceJson, lupusec)
    else:
        _LOGGER.info("Device is not known")
    return None
