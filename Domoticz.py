"""For controlling Domoticz."""
from urllib.request import urlopen
import json
import re

class Domoticz:
    """Class for controlling Domoticz."""
    def __init__(self, host, port, protocol, authentication, login, password):
        """Recover settings for accessing to Domoticz instance."""
        self.host = host
        self.port = port
        self.protocol = protocol
        self.authentication = authentication
        if protocol:
            self.protocol = "http"
        else:
            self.protocol = "https"
        if authentication:
            self.login = login
            self.password = password
            self.url = self.protocol + "://" + self.login + ":" + self.password + "@" + self.host + ":" + self.port
        else:
            self.url = self.protocol + "://" + self.host + ":" + self.port

    def findid(self, what, where, state):
        i = 0
        wht = re.compile(what, re.I)
        whr = re.compile(where, re.I)
        f = urlopen(self.url + "/json.htm?type=devices&filter=all&used=true")
        response = f.read()
        payload = json.loads(response.decode('utf-8'))
        idx = False
        stype = False
        dlevel = False
        maxdlevel = False
        while i < len(payload['result']):
            if whr.search(payload['result'][i]['Name']) and wht.search(payload['result'][i]['Name']):
                stype = payload['result'][i]['Type']
                typ = re.compile(stype, re.I)
                if typ.search("Group") or typ.search("Scene"):
                    stype = "scene"
                    dlevel = " "
                    maxdlevel = " "
                    idx = payload['result'][i]['idx']
                    rslt = re.compile(" " + str(state).title(), re.I)
                    if rslt.search(" " + payload['result'][i]['Status']):
                        result = 0
                    else:
                        result = 1
                    break
                else:
                    stype = "light"
                    dlevel = payload['result'][i]['LevelInt']
                    maxdlevel = payload['result'][i]['MaxDimLevel']
                idx = payload['result'][i]['idx']
                rslt = re.compile(" " + str(state).title(), re.I)
                if rslt.search(" " + payload['result'][i]['Data']):
                    result = 0
                else:
                    result = 1
                break
            elif i is len(payload['result']) - 1:
                result = None
                break
            i += 1
        return [idx, result, stype, dlevel, maxdlevel]

    def findcmd(self, state, action, dlevel, maxdlevel):
        dsrdst = str(state).title()
        act = str(action).title()
        rslt = re.compile(dsrdst, re.I)
        rslt2 = re.compile(act, re.I)
        if dsrdst.find('%') > -1:
            if len(dsrdst) == 3:
                dsrdst = int(dsrdst[0:2])
            elif len(dsrdst) == 4:
                dsrdst = 100
            else:
                dsrdst = 5
        cmd = dsrdst
        if (rslt2.search('decrease') or rslt2.search('dimmer') or rslt2.search('dim')):
            stlvl = int(dlevel) - (int(dlevel) / 100 * int(dsrdst))
            if stlvl < 0:
                stlvl = 0
            cmd = "Set%20Level&level=" + str(stlvl)
        elif (rslt2.search('increase') or rslt2.search('brighter') or rslt2.search('brighten')):
            stlvl = int(dlevel) + (int(dlevel) / 100 * int(dsrdst))
            if stlvl > 100:
                stlvl = 100
            cmd = "Set%20Level&level=" + str(stlvl)
        elif rslt2.search('set'):
            stlvl = int(maxdlevel) / 100 * int(cmd)
            if stlvl > 100:
                stlvl = int(maxdlevel)
            elif stlvl < 0:
                stlvl = 0
            cmd = "Set%20Level&level=" + str(stlvl)
        else:
            if rslt.search('lock') or rslt.search('open') or rslt.search('on'):
                cmd = "On"
            elif rslt.search('unlock') or rslt.search('close') or rslt.search('off'):
                cmd = "Off"
        return cmd

    def switch(self, state, what, where, action):
        """Switch the device in Domoticz."""
        data = []
        data = self.findid(what, where, state)
        idx = data[0]
        result = data[1]
        stype = data[2]
        dlevel = data[3]
        maxdlevel = data[4]
        if result is 1:
            cmd = self.findcmd(state, action, dlevel, maxdlevel)
            if cmd:
                try:
                    f = urlopen(self.url + "/json.htm?type=command&param=switch" + stype + "&idx=" + str(idx) + "&switchcmd=" + str(cmd))
                    response = f.read()
                    return response
                except IOError as e:
                    return result
            else:
                return result
        else:
             return result
        return result

    def get(self, what, where):
        """Get the device's data in Domoticz."""
        try:
            f = urlopen(self.url + "/json.htm?type=devices&filter=all&used=true")
            response = f.read()
            payload = json.loads(response.decode('utf-8'))
            wht = re.compile(what, re.I)
            i = 0
            if where is not None:
                whr = re.compile(where, re.I)
                while i < len(payload['result']):
                    if whr.search(payload['result'][i]['Name']) and wht.search(payload['result'][i]['Name']):
                        break
                    elif i is len(payload['result']) - 1:
                        payload['result'][i]['Data'] = None
                        break
                    i += 1
            elif where is None:
                while i < len(payload['result']):
                    if wht.search(payload['result'][i]['Name']):
                        break
                    elif i is len(payload['result']) - 1:
                        payload['result'][i]['Data'] = None
                        break
                    i += 1
            return payload['result'][i]
        except IOError as e:
            return result
