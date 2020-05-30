import os
import time
from eoscrypto import EOSCryptoAccount

active_privat_key = os.environ['WINE_VENDOR_PRIVAT_KEY']
price = [{'code': 'eosio.token', 'symbol': 'EOS', 'amount': 0.5639},
         {'code': 'knygarium111', 'symbol': 'KNYGA', 'amount': 50}]

bartender_account = EOSCryptoAccount('wealthysnake', 'http://jungle.atticlab.net:8888',
                                     'https://junglehistory.cryptolions.io', active_privat_key, price)
print(bartender_account.get_actions())
# print(bartender_account.last_global_sequence)
# bartender_account.send_tokens('wealthytiger', 0.007, 'EOS', 'for wine transaction #')
bartender_account.send_tokens('winecustomer', 0.0021, 'EOS', 'Not enough money sent. The price is 0.5639 EOS')
# print('sent')
i = 0
while True:
    new_payments = bartender_account.get_new_payments()
    if new_payments:
        print(new_payments)
    # print(i)
    i += 1
    time.sleep(5)
