import os
import time
from eoscrypto import EOSCryptoAccount

active_privat_key = os.environ['WINE_VENDOR_PRIVAT_KEY']
price = [{'code': 'eosio.token', 'symbol': 'EOS', 'amount': 0.5639},
         {'code': 'knygarium111', 'symbol': 'KNYGA', 'amount': 50}]

delay_max = 21  # sec - it's max delay from device
vendor_account = 'wealthytiger'
vendor_part = 0.4
owner_account = 'cryptotexty1'
owner_part = 0.4
support_account = 'destitutecat'
support_part = 1 - vendor_part - owner_part

bartender_account = EOSCryptoAccount('wealthysnake',
                                     'http://jungle.atticlab.net:8888',
                                     'https://junglehistory.cryptolions.io',
                                     active_privat_key, price)
