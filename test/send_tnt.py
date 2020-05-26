import os
import json
import time
import paho.mqtt.client as mqtt
from eospy.cleos import Cleos
import eospy.cleos
import eospy.keys
import pytz
import requests

eos_endpoint = 'https://api.testnet.eos.io'
bartender_account = 'gaxdyyrkwguk'
active_privat_key = os.environ['WINE_VENDOR_PRIVAT_KEY']

def send_tokens(token, account_to, quantity, memo):
    # contract_accounts = {'EOS': 'eosio.token', 'KNYGA': 'knygarium111'}
    contract_accounts = {'TNT': 'eosio.token', 'KNYGA': 'knygarium111'}
    ce = Cleos(url=eos_endpoint)
    quantity_str = str(quantity)
    qs_start = quantity_str[:quantity_str.find('.')]
    qs_end = quantity_str[quantity_str.find('.'):]
    needs_0 = 5 - len(qs_end)
    if needs_0 < 0:
        qs_end = qs_end[:5]
    n = 0
    while n < needs_0:
        n += 1
        qs_end = qs_end + '0'
    quantity_str = qs_start + qs_end
    arguments = {
        "from": bartender_account,  # sender
        "to": account_to,  # receiver
        "quantity": quantity_str + ' ' + token,  # In Token
        "memo": memo,
    }
    payload = {
        "account": contract_accounts[token],
        "name": 'transfer',
        "authorization": [{
            "actor": bartender_account,
            "permission": 'active',
        }],
    }
    # Converting payload to binary
    data = ce.abi_json_to_bin(payload['account'], payload['name'], arguments)
    # Inserting payload binary form as "data" field in original payload
    payload['data'] = data['binargs']
    # final transaction formed
    trx = {"actions": [payload]}
    import datetime as dt
    trx['expiration'] = str((dt.datetime.utcnow() + dt.timedelta(seconds=60)).replace(tzinfo=pytz.UTC))
    key = eospy.keys.EOSKey(active_privat_key)
    resp = ce.push_transaction(trx, key, broadcast=True)
    if ('transaction_id' in resp.keys()):
        return float(quantity_str)
    else:

        return 0

token = 'TNT'
receiver_account = 'pawhjmizyyqy'
sum_for_send = '0.5'
transfer_memo = 'test memo'
print(send_tokens(token, receiver_account, sum_for_send,transfer_memo))
