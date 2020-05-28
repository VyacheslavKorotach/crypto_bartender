import json
import time
import paho.mqtt.client as mqtt


class Vmachine:
    __topic_sub = ''
    __topic_pub = ''
    __mqtt_host = ''
    __mqtt_user = ''
    __mqtt_password = ''
