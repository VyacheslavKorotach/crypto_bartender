import json
import time
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
        self._status = 'Off'

        self.activity_period = 60  # time (in seconds) to consider the device is inactive
        self.processing_period = 30  # time (in seconds) to consider the device can't execute command

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
        self._mqttc.loop_start()

    def status(self):
        delta = dt.datetime.utcnow() - self._last_ping_time
        if delta.seconds > self.activity_period:
            self._status = 'Off'
        return self._status  # can be 'Off', 'Reset', 'Ready', 'Busy', 'Ok' or 'Error'

    def reset(self):
        self._mqttc.publish(self._topic_pub, '{"code": "reset"}')
        self._status = 'Reset'

    def ping(self):
        self._mqttc.publish(self._topic_pub, '{"code": "ping"}')

    def give_the_goods(self, customer: str):
        self._mqttc.publish(self._topic_pub, f'{{"code": "give_the_goods", "customer": "{customer}"}}')
        self._status = 'Busy'
        start_time = dt.datetime.utcnow()
        delta = dt.datetime.utcnow() - start_time
        while self._status == 'Busy' and delta.seconds < self.processing_period:
            time.sleep(1)
            delta = dt.datetime.utcnow() - start_time
            print(f'processing {delta.seconds}')
        if self._status == 'Ok':
            self.reset()
            return True
        else:
            self._status = 'Error'
            return False

    def on_connect(self, mosq, obj, flags, rc):
        self._mqttc.subscribe(self._topic_sub, 0)
        print("rc: " + str(rc))

    def on_message(self, mosq, obj, msg):
        """
        get the status string from device
        {"status": "Ok"} or {"status": "Error"} or {"status": "Busy"}
        or {"status": "Ready"}
        """
        print(f'{msg.topic} {str(msg.qos)} {str(msg.payload)}')
        self._last_ping_time = dt.datetime.utcnow()  # got a ping
        self.ping()
        json_string = ''
        d = {}
        try:
            json_string = msg.payload.decode('utf8')
        except UnicodeDecodeError:
            print("it was not an ASCII encoded Unicode string")
        if json_string != '' and self.is_json(json_string):
            d = json.loads(json_string)
            if 'status' in d.keys():
                self._status = d['status']
                print(self._status)

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
