import json
from eospy.cleos import Cleos
import eospy.cleos
import eospy.keys
import pytz
import requests


class EOSCryptoAccount:
    __account = ''
    __api_endpoint = ''
    __history_endpoint = ''
    __depth = 8
    __active_privat_key = ''
    __last_global_sequence = 0
    __balance = [{}]
    __last_actions = {}

    def __init__(self, account: str, api_endpoint: str, history_endpoint: str, active_privat_key: str, currencies):
        self.__account = account
        self.__api_endpoint = api_endpoint
        self.__history_endpoint = history_endpoint
        self.__active_privat_key = active_privat_key
        self.__last_actions = self.get_actions()
        self.__currencies = dict()
        for currency in currencies:
            self.__currencies[currency['symbol']] = currency['code']

    def get_actions(self):
        request_str = self.__history_endpoint + '/v2/history/get_actions?limit=' + \
                      str(self.__depth) + '&account=' + self.__account

        response = requests.get(request_str)
        response_json = response.json()
        if request_str:
            self.__last_global_sequence = response_json['actions'][0]['global_sequence']
        return response_json

    def get_new_payments(self):
        old_last_sequence = self.__last_global_sequence
        actions_json = self.get_actions()
        new_payments = []
        i = 0
        while actions_json['actions'][i]['global_sequence'] > old_last_sequence:
            if actions_json['actions'][i]['act']['name'] == 'transfer' and \
                    self.__currencies[actions_json['actions'][i]['act']['data']['symbol']] == \
                    actions_json['actions'][i]['act']['account'] and \
                    actions_json['actions'][i]['act']['data']['to'] == self.__account:
                new_payments.append(actions_json['actions'][i])
            i += 1
        return new_payments

    def send_tokens(self, token, account_to, amount, memo):
        ce = Cleos(url=self.__api_endpoint)
        quantity_str = str(amount)
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
            "from": self.__account,  # sender
            "to": account_to,  # receiver
            "quantity": quantity_str + ' ' + token,  # In Token
            "memo": memo,
        }
        payload = {
            "account": self.__currencies[token],
            "name": 'transfer',
            "authorization": [{
                "actor": self.__account,
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
        key = eospy.keys.EOSKey(self.__active_privat_key)
        resp = ce.push_transaction(trx, key, broadcast=True)
        if 'transaction_id' in resp.keys():
            print(f'{amount} {token} sent to {account_to}')
            return float(quantity_str)
        else:
            print(f'error sending {amount} {token} to {account_to}')
            return 0
