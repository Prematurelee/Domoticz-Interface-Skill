#!/usr/bin/python

from Domoticz import Domoticz

hostname = "192.168.0.103"
port = "8080"
protocol = "http"
authentication = ""
username = ""
password = ""
state = "on"
what = "lights"
where = "all the"
action = "turn"

domoticz = Domoticz(hostname, port, protocol, authentication, username, password)

domoticz.switch(state, what, where, action)
