import os
import time
from vmachine import VMachine

# topic_sub = 'cryptobartender/state/device_name'
# topic_pub = 'cryptobartender/ctl/device_name'

bartender_device0001 = VMachine('device0001', os.environ['WINE_VENDOR_MQTT_HOST'],
                                1883, os.environ['WINE_VENDOR_MQTT_USER'],
                                os.environ['WINE_VENDOR_MQTT_PASSWORD'],
                                'cryptobartender/state', 'cryptobartender/ctl')
time.sleep(1)
bartender_device0001.reset()
bartender_device0001.activity_period = 3
time.sleep(1)
if bartender_device0001.give_the_goods('vasya'):
    print("That's all right")
else:
    print('Error')
while True:
    print(bartender_device0001.status())
    time.sleep(1)

