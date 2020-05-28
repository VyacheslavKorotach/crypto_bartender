import os
from .eoscrypto import EOSCryptoAccount

active_privat_key = os.environ['WINE_VENDOR_PRIVAT_KEY']
balance = [{'code': 'eosio.token', 'symbol': 'EOS', 'amount': 0},
           {'code': 'knygarium111', 'symbol': 'KNYGA', 'amount': 0}]
