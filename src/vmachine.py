import json
import paho.mqtt.client as mqtt
import datetime as dt


class VMachine:
    def __init__(self, device_name: str, mqtt_host: str, mqtt_port: int, mqtt_user: str,
                 mqtt_password: str, topic_sub: str, topic_pub: str):
        self._mqtt_host = mqtt_host
        self._mqtt_port = mqtt_port
        self._mqtt_user = mqtt_user
        self._mqtt_password = mqtt_password
        self._topic_sub = f'{topic_sub}/{device_name}'
        self._topic_pub = f'{topic_pub}/{device_name}'
        self._last_ping_time = dt.datetime(1974, 7, 21)  # author's birthday :)
        self._activity_period = 15  # time (in seconds) to consider the device as inactive
        self._status = 'Off'

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

    def status(self):
        delta = dt.datetime.utcnow() - self._last_ping_time
        if delta.seconds > self._activity_period:
            self._status = 'Off'
        # return f'Ready {dt.datetime.utcnow()} delta is {delta.seconds}'
        return self._status

    def on_connect(self, mosq, obj, flags, rc):
        self._mqttc.subscribe(self._topic_sub, 0)
        print("rc: " + str(rc))

    def on_message(self, mosq, obj, msg):
        """
        get the status string from device
        {"recv_sequence": 32, "status": "OK"} or {"recv_sequence": 32, "status": "Error"}
        or {"status": "Restart"}
        """
        # global state
        self._status = 'Ready'
        print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
        self._last_ping_time = dt.datetime.utcnow()
        json_string = ''
        d = {}
        try:
            json_string = msg.payload.decode('utf8')
        except UnicodeDecodeError:
            print("it was not a ascii-encoded unicode string")
        print('json_string = ', json_string)
        if json_string != '' and self.is_json(json_string):
            d = json.loads(json_string)
            if 'status' in d.keys():
                if d['status'].find('OK') != -1 \
                        and 'recv_sequence' in d.keys() and d['recv_sequence'] == goods_number:
                    self._status = 'we successfully have gave goods out'
                elif d['status'].find('Error') != -1:
                    self._status = 'We have received the Error code from device.'
                elif d['status'].find('Restart') != -1:
                    self._status = 'Restart'
                elif d['status'].find('Empty') != -1:
                    self._status = 'Crypto-vendor is empty.'
                    pass
                elif d['status'].find('Ready') != -1:
                    self._status = 'Crypto-vendor is ready.'
                    pass
                elif d['status'].find('Busy') != -1:
                    self._status = 'Crypto-vendor is busy.'
                    pass
                elif d['status'].find('NO CONNECT') != -1:
                    self._status = 'NO CONNECT'
                    pass
                else:
                    self._status = 'We have received a wrong message from device. Stop crypto-bartender.'
            else:
                self._status = 'We have received a wrong message from device. Stop crypto-bartender.'

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
