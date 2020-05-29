from eospy.cleos import Cleos
import eospy.cleos
import eospy.keys
import pytz
import requests


class EOSCryptoAccount:
    def __init__(self, account: str, api_endpoint: str, history_endpoint: str, active_privat_key: str, currencies):
        self._depth = 8
        self._last_global_sequence = 0
        self._account = account
        self._api_endpoint = api_endpoint
        self._history_endpoint = history_endpoint
        self._active_privat_key = active_privat_key
        self.get_actions()
        self._currencies = dict()
        for currency in currencies:
            self._currencies[currency['symbol']] = currency['code']

    def get_actions(self):
        request_str = self._history_endpoint + '/v2/history/get_actions?limit=' + \
                      str(self._depth) + '&account=' + self._account

        response = requests.get(request_str)
        response_json = response.json()
        if request_str:
            self._last_global_sequence = response_json['actions'][0]['global_sequence']
        return response_json

    def get_new_payments(self):
        old_last_sequence = self._last_global_sequence
        actions_json = self.get_actions()
        new_payments = []
        i = 0
        while actions_json['actions'][i]['global_sequence'] > old_last_sequence:
            if actions_json['actions'][i]['act']['name'] == 'transfer' and \
                    self._currencies[actions_json['actions'][i]['act']['data']['symbol']] == \
                    actions_json['actions'][i]['act']['account'] and \
                    actions_json['actions'][i]['act']['data']['to'] == self._account:
                # new_payments.append(actions_json['actions'][i])
                new_payments.append(actions_json['actions'][i]['act']['data'])
            i += 1
        return new_payments

    def send_tokens(self, token, account_to, amount, memo):
        ce = Cleos(url=self._api_endpoint)
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
            "from": self._account,  # sender
            "to": account_to,  # receiver
            "quantity": quantity_str + ' ' + token,  # In Token
            "memo": memo,
        }
        payload = {
            "account": self._currencies[token],
            "name": 'transfer',
            "authorization": [{
                "actor": self._account,
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
        key = eospy.keys.EOSKey(self._active_privat_key)
        resp = ce.push_transaction(trx, key, broadcast=True)
        if 'transaction_id' in resp.keys():
            print(f'{amount} {token} sent to {account_to}')
            return float(quantity_str)
        else:
            print(f'error sending {amount} {token} to {account_to}')
            return 0
