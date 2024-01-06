from mycroft import MycroftSkill, intent_file_handler, intent_handler
from adapt.intent import IntentBuilder
from mycroft.util.log import getLogger
from os.path import dirname, abspath
from .Domoticz import Domoticz
import sys
import re


sys.path.append(abspath(dirname(__file__)))
LOGGER = getLogger(__name__)

class DomoticzInterface(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_handler(IntentBuilder('SwitchIntent')
                    .optionally('TurnKeyword')
                    .require('StateKeyword')
                    .require('WhatKeyword')
                    .require('WhereKeyword'))

    def handle_domoticz_switch_intent(self, message):
        domoticz = Domoticz(
            self.settings.get("hostname"),
            self.settings.get("port"),
            self.settings.get("protocol"),
            self.settings.get("authentication"),
            self.settings.get("username"),
            self.settings.get("password"))
        state = message.data.get("StateKeyword")
        what = message.data.get("WhatKeyword")
        where = message.data.get("WhereKeyword")
        action = message.data.get("TurnKeyword")
        data = {
            'what': what,
            'where': where
        }
        if state == "open":
            state = "Off"
            action = "open"
        if state == "close":
            state = "On"
            action = "close"
        response = domoticz.switch(state, what, where, action)
        edng = re.compile(str(state).title(), re.I)
        ending = "ed"
        if edng.search('on') or edng.search('off'):
            ending = ""
        if response is None:
            if where is None:
                self.speak_dialog("NotFoundShort", data)
            else:
                self.speak_dialog("NotFound", data)
        if response is 0:
            if "lights" in what:
                self.speak("The " + str(what) + " are already " + str(state).title() + ending)
            else:
                self.speak("The " + str(what) + " is already " + str(state).title() + ending)
        elif response is 1:
            self.speak("The " + str(what) + " can not be operated with " + str(state).title())
        if state == "on" and not response is None and not response is 0 and not response is 1:
            self.speak_dialog("affirm_on", data)
        if state == "off" and not response is None and not response is 0 and not response is 1:
            self.speak_dialog("affirm_off", data)
        if action == "open" and not response is None and not response is 0 and not response is 1:
            self.speak_dialog("affirm_open", data)
        if action == "close" and not response is None and not response is 0 and not response is 1:
            self.speak_dialog("affirm_close", data)



    @intent_handler(IntentBuilder("InfosIntent")
                    .require("InfosKeyword")
                    .require("WhatKeyword")
                    .optionally("WhereKeyword")
                    .optionally("StateKeyword"))

    def handle_domoticz_infos_intent(self, message):
        what = message.data.get("WhatKeyword")
        where = message.data.get("WhereKeyword")
        domoticz = Domoticz(
            self.settings.get("hostname"),
            self.settings.get("port"),
            self.settings.get("protocol"),
            self.settings.get("authentication"),
            self.settings.get("username"),
            self.settings.get("password"))
        data = {
            'what': what,
            'where': where
        }

        response = domoticz.get(what, where)
        data = str(response['Data'])
        if data is None:
            if where is None:
                self.speak_dialog("NotFoundShort", data)
            else:
                self.speak_dialog("NotFound", data)
        if re.search('\d\s+C', data):
            data = data.replace(' C', ' degrees celsius')
        if re.search('\d\s+F', data):
            data = data.replace(' F', ' degrees fahrenheit')
        data = "It's " + data
        LOGGER.debug("result : " + str(data))
        self.speak(str(data))

def create_skill():
    return DomoticzInterface()

