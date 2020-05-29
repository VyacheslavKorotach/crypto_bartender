import json
import time
import paho.mqtt.client as mqtt


class Vmachine:
    def __init__(self, mqtt_host: str, mqtt_port: str, mqtt_user: str, mqtt_password: str,
                 topic_sub: str, topic_pub: str):
        self._mqtt_host = mqtt_host
        self._mqtt_port = mqtt_port
        self._mqtt_user = mqtt_user
        self._mqtt_password = mqtt_password
        self._topic_sub = topic_sub
        self._topic_pub = topic_pub

        self._mqttc = mqtt.Client()
        # Assign event callbacks
        self._mqttc.on_message = self.on_message
        self._mqttc.on_connect = self.on_connect
        self._mqttc.on_publish = self.on_publish
        self._mqttc.on_subscribe = self.on_subscribe
        # mqttc.on_log = on_log
        self._mqttc.username_pw_set(mqtt_user, password=mqtt_password)
        # Connect
        self._mqttc.connect(mqtt_host, mqtt_port, 60)
        # Continue the network loop
        # mqttc.loop_forever()
        self._mqttc.loop_start()

    def on_connect(self, mosq, obj, flags, rc):
        self._mqttc.subscribe(self._topic_sub, 0)
        print("rc: " + str(rc))

    def on_message(self, mosq, obj, msg):
        """
        get the status string from device
        {"recv_sequence": 32, "status": "OK"} or {"recv_sequence": 32, "status": "Error"}
        or {"status": "Restart"}
        """
        global state
        print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
        json_string = ''
        d = {}
        try:
            json_string = msg.payload.decode('utf8')
        except UnicodeDecodeError:
            print("it was not a ascii-encoded unicode string")
        if debug: print('json_string = ', json_string)
        if json_string != '' and self.is_json(json_string):
            d = json.loads(json_string)
            if 'status' in d.keys():
                if d['status'].find('OK') != -1 \
                        and 'recv_sequence' in d.keys() and d['recv_sequence'] == goods_number:
                    state = 'we successfully have gave goods out'
                elif d['status'].find('Error') != -1:
                    state = 'We have received the Error code from device.'
                elif d['status'].find('Restart') != -1:
                    state = 'Restart'
                elif d['status'].find('Empty') != -1:
                    state = 'Crypto-vendor is empty.'
                    pass
                elif d['status'].find('Ready') != -1:
                    state = 'Crypto-vendor is ready.'
                    pass
                elif d['status'].find('Busy') != -1:
                    state = 'Crypto-vendor is busy.'
                    pass
                elif d['status'].find('NO CONNECT') != -1:
                    state = 'NO CONNECT'
                    pass
                else:
                    state = 'We have received a wrong message from device. Stop crypto-bartender.'
            else:
                state = 'We have received a wrong message from device. Stop crypto-bartender.'

    #    if debug: print('state = ', state)

    def on_publish(self, mosq, obj, mid):
        print("mid: " + str(mid))

    def on_subscribe(self, mosq, obj, mid, granted_qos):
        print("Subscribed: " + str(mid) + " " + str(granted_qos))

    def on_log(self, mosq, obj, level, string):
        print(string)

    def is_json(self, myjson):
        try:
            json_object = json.loads(myjson)
        except ValueError:
            return False
        return True
