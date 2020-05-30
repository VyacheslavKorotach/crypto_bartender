import time
from vmachine import VMachine
from eoscrypto import EOSCryptoAccount


class IoTEOSCommunicator:
    def __init__(self, account: EOSCryptoAccount, vmachine: VMachine):
        self._account = account
        self._vmachine = vmachine

    def sell_goods_according_to_price(self, price):
        income = dict()
        print('waiting for new payments')
        new_payments = self._account.get_new_payments()
        while not new_payments:
            time.sleep(3)
            new_payments = self._account.get_new_payments()
        for payment in new_payments:
            print(payment)
            symbol = ''
            currency_num = 0
            for p in price:
                if p['symbol'] == payment['symbol']:
                    symbol = payment['symbol']
                    break
                currency_num += 1
            if symbol == '':
                return {}
            amount = payment['amount']
            customer = payment['from']
            goods_price = price[currency_num]['amount']
            if amount < goods_price:
                memo = f'Not enough money sent. The price is {goods_price} {symbol}'
                self._account.send_tokens(customer, amount, symbol, memo)
            elif amount > goods_price:
                memo = f'Too much money sent. The price is {goods_price} {symbol}'
                if self._vmachine.give_the_goods(customer):
                    self._account.send_tokens(customer, amount - goods_price, symbol, memo)
                    income['symbol'] = symbol
                    income['amount'] = goods_price
                    print(f'we have {goods_price} {symbol} income')
                else:  # something went wrong. refund all money.
                    self._account.send_tokens(customer, amount, symbol, memo)
            else:  # amount == goods_price
                if self._vmachine.give_the_goods(customer):
                    memo = 'Thank you! Have a nice day! :)'
                    self._account.send_tokens(customer, 0.0001, symbol, memo)
                    income['symbol'] = symbol
                    income['amount'] = goods_price - 0.0001
                    print(f'we have {goods_price - 0.0001} {symbol} income')
                else:  # something went wrong. refund all money.
                    memo = 'Something went wrong :('
                    self._account.send_tokens(customer, amount, symbol, memo)
        return income

    def share_income_according_to_agreement(self, income, share_agreement):
        pass
        return True
