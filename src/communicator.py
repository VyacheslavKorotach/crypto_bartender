import time
from vmachine import VMachine
from eoscrypto import EOSCryptoAccount


class IoTEOSCommunicator:
    def __init__(self, account: EOSCryptoAccount, vmachine: VMachine):
        self._account = account
        self._vmachine = vmachine

    def sell_goods_according_to_price(self, price):
        income = {}
        print('waiting for new payments')
        new_payments = self._account.get_new_payments()
        while not new_payments:
            time.sleep(3)
            new_payments = self._account.get_new_payments()
        for payment in new_payments:
            print(payment)
        return income

    def share_income_according_to_agreement(self, income, share_agreement):
        pass
        return True
