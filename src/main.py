import os
import time
from eoscrypto import EOSCryptoAccount
from vmachine import VMachine
from communicator import IoTEOSCommunicator

price = [{'code': 'eosio.token', 'symbol': 'EOS', 'amount': 0.5639},
         {'code': 'eosio.token', 'symbol': 'JUNGLE', 'amount': 50}]
# price = [{'code': 'eosio.token', 'symbol': 'EOS', 'amount': 0.5639},
#          {'code': 'eosio.token', 'symbol': 'JUNGLE', 'amount': 50},
#          {'code': 'winecustomer', 'symbol': 'KNYGA', 'amount': 50}]

share_agreement = {'wealthytiger': 0.4, 'cryptotexty1': 0.4, 'destitutecat': 0.2}
# vendor account - 'wealthytiger'  vendor part - 40% * income
# landlord account - 'cryptotexty1'  landlord part - 40% * income
# support account - 'destitutecat' support part - 20% * income - 0.0001 EOS

bartender_account = EOSCryptoAccount('wealthysnake',
                                     'http://jungle.atticlab.net:8888',
                                     'https://junglehistory.cryptolions.io',
                                     os.environ['WINE_VENDOR_PRIVAT_KEY'], price)

# topic_sub = 'cryptobartender/state/device_name'
# topic_pub = 'cryptobartender/ctl/device_name'
bartender_device0001 = VMachine('device0001', os.environ['WINE_VENDOR_MQTT_HOST'],
                                1883, os.environ['WINE_VENDOR_MQTT_USER'],
                                os.environ['WINE_VENDOR_MQTT_PASSWORD'],
                                'cryptobartender/state', 'cryptobartender/ctl')

bartender = IoTEOSCommunicator(bartender_account, bartender_device0001)

while True:
    income = bartender.sell_goods_according_to_price(price)
    time.sleep(0.1)
    if income:
        bartender.share_income_according_to_agreement(income, share_agreement)
