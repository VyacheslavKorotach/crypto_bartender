import os
import json
import time
import paho.mqtt.client as mqtt
from eospy.cleos import Cleos
import eospy.cleos
import eospy.keys
import pytz
import requests

# eos_endpoint = 'https://eosbp.atticlab.net'  # last working
# eos_endpoint = 'https://api.testnet.eos.io'
# eos_endpoint = 'https://testnet.eos.dfuse.io/'
# eos_endpoint = 'http://213.202.230.42:8888'
# eos_endpoint = 'http://jungle.eosphere.io:443'
# eos_endpoint = 'http://junglehistory.cryptolions.io:18888'
# eos_endpoint = 'https://api.jungle.alohaeos.com' #history OK
# eos_endpoint = 'http://145.239.133.201:8888'
# eos_endpoint = 'http://junglehistory.cryptolions.io'
eos_endpoint = 'http://jungle.atticlab.net:8888'
# eos_endpoint = 'http://145.239.133.201:8888'
# bartender_account = 'gaxdyyrkwguk'
bartender_account = 'wealthysnake'
# bartender_account = 'eosmechanics'
active_privat_key = os.environ['WINE_VENDOR_PRIVAT_KEY']


def send_tokens(token, account_to, quantity, memo):
    # contract_accounts = {'EOS': 'eosio.token', 'KNYGA': 'knygarium111'}
    contract_accounts = {'TNT': 'eosio.token', 'EOS': 'eosio.token', 'KNYGA': 'knygarium111'}
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


def get_EOS_balance(account):
    ce = Cleos(url=eos_endpoint)
    try:
        EOS_balance_list = ce.get_currency_balance(account)
        EOS_balance = float(EOS_balance_list[0].split(' ')[0])
    except (requests.exceptions.HTTPError,
            requests.exceptions.ConnectionError,
            requests.exceptions.ReadTimeout,
            json.decoder.JSONDecodeError):
        print("Can't get EOS balance")
        EOS_balance = float(0)
    return EOS_balance


# token = 'TNT'
token = 'EOS'
# receiver_account = 'pawhjmizyyqy'
# receiver_account = 'gaxdyyrkwguk'
receiver_account = 'wealthytiger'
sum_for_send = '0.0887'
transfer_memo = 'test memo'
# print(send_tokens(token, receiver_account, sum_for_send,transfer_memo))
# ce = Cleos(url=eos_endpoint)
# actions = ce.get_actions(bartender_account, pos=-1, offset=-20)
# actions = ce.get_actions(receiver_account, pos=-1, offset=-20)
# print(actions)
print(get_EOS_balance(receiver_account))

response = requests.get('https://junglehistory.cryptolions.io/v2/history/get_actions?limit=1&account=wealthysnake')
print(response)
print(response.json())
print(response.json()['actions'][0]['act']['data'])
print(response.json()['actions'][0]['act']['data']['from'])
print(response.json()['actions'][0]['act']['data']['to'])
print(response.json()['actions'][0]['act']['data']['amount'])
print(response.json()['actions'][0]['act']['data']['symbol'])
print(response.json()['actions'][0]['global_sequence'])
