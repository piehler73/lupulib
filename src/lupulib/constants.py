# Constants for Lupusec Alarm System

# Used in setup.py
# -*- coding: utf-8 -*-
VERSION = "0.3.10"
PROJECT_PACKAGE_NAME = "lupulib"
PROJECT_LICENSE = "MIT"
PROJECT_URL = "http://www.github.com/majuss/lupulib"
PROJECT_DESCRIPTION = "A python cli for Lupusec alarm panels."
PROJECT_LONG_DESCRIPTION = (
    "lupulib is a python3 interface for"
    " the Lupus Electronics alarm panel."
    " Its intented to get used in various"
    " smart home services to get a full"
    " integration of all you devices."
)
PROJECT_AUTHOR = "Majuss"


# Lupusec API Calls: Requests and Headers
URL_HTTP = "http://"
URL_ACTION = "/action/"
LOGIN_REQUEST = "login"
INFO_REQUEST = "welcomeGet"
INFO_HEADER = "updates"

HISTORY_REQUEST = "historyGet"
HISTORY_ALARM_COLUMN = "a"
HISTORY_HEADER = "hisrows"
HISTORY_CACHE_NAME = ".lupusec_history_cache"


# Lupusec System Info
SYS_HW_VERSION = "rf_ver"
SYS_SW_VERSION = "em_ver"
SYS_GSM_VERSION = "gsm_ver"
SYS_IP_ADDRESS = "ip"
SYS_MAC_ADDRESS = "mac"


# Lupusec System and Device status
STATUS_ON_INT = 0
STATUS_ON = "on"
STATUS_OFF_INT = 1
STATUS_OFF = "off"
STATUS_OFFLINE = "offline"
STATUS_CLOSED = "Geschlossen"
STATUS_CLOSED_INT = 0
STATUS_OPEN = "Offen"
STATUS_OPEN_INT = 1

ALARM_NAME = "Lupusec Alarm"
ALARM_DEVICE_ID = "0"
ALARM_TYPE = "Alarm"


# GENERIC Lupusec DEVICE TYPES
TYPE_WINDOW = "Fensterkontakt"
TYPE_DOOR = "Türkontakt"
TYPE_CONTACT_XT2 = 4
TYPE_WATER_XT2 = 5
TYPE_SMOKE_XT2 = 11
TYPE_POWER_SWITCH_1_XT2 = 24
TYPE_POWER_SWITCH_2_XT2 = 25
TYPE_POWER_SWITCH = "Steckdose"
TYPE_SWITCH = [TYPE_POWER_SWITCH, TYPE_POWER_SWITCH_1_XT2, TYPE_POWER_SWITCH_2_XT2]
TYPE_OPENING = [TYPE_DOOR, TYPE_WINDOW, TYPE_CONTACT_XT2]
BINARY_SENSOR_TYPES = TYPE_OPENING
TYPE_SENSOR = ["Rauchmelder", "Wassermelder", TYPE_WATER_XT2, TYPE_SMOKE_XT2]
TYPE_TRANSLATION = {
    "Fensterkontakt": "window",
    "Türkontakt": "door",
    TYPE_CONTACT_XT2: "Fenster-/Türkontakt",
    TYPE_WATER_XT2: "Wassermelder",
    TYPE_SMOKE_XT2: "Rauchmelder",
}
DEVICES_API_XT1 = "sensorListGet"
DEVICES_API_XT2 = "deviceListGet"


# Alarm Modes and Zones
MODE_AWAY = "Arm"
MODE_HOME = "Home"
MODE_DISARMED = "Disarm"
MODE_ALARM_TRIGGERED = "Einbruch"
ALL_MODES = [MODE_DISARMED, MODE_HOME, MODE_AWAY]
MODE_TRANSLATION_XT1 = {"Disarm": 2, "Home": 1, "Arm": 0}
MODE_TRANSLATION_XT2 = {"Disarm": 0, "Arm": 1, "Home": 2}
XT2_MODES_TO_TEXT = {
    "{AREA_MODE_0}": "Disarm",
    "{AREA_MODE_1}": "Arm",
    "{AREA_MODE_2}": "Home",
    "{AREA_MODE_3}": "Home",
    "{AREA_MODE_4}": "Home",
}

STATE_ALARM_DISARMED = "disarmed"
STATE_ALARM_ARMED_HOME = "armed_home"
STATE_ALARM_ARMED_AWAY = "armed_away"
STATE_ALARM_TRIGGERED = "alarm_triggered"
MODE_TRANSLATION_GENERIC = {
    "Disarm": "disarmed",
    "Home": "armed_home",
    "Arm": "armed_away",
}
DEFAULT_MODE = MODE_AWAY

