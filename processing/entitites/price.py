from price_parser import Price

from processing.interfaces import BaseItem


class GustmarketPrice(BaseItem):
    amount: float
    currency: str

    def __init__(self, amount, currency=None):
        self.amount = amount
        self.currency = currency

    def __str__(self):
        return f"GustmarketPrice({self.amount}, {self.currency})"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.amount == other.amount and self.currency == other.currency

    def __hash__(self):
        return hash((self.amount, self.currency))

    def to_json(self):
        return {
            "amount": self.amount,
            "currency": self.currency,
        }

    @staticmethod
    def from_json(json):
        if json is None:
            return None
        return GustmarketPrice(
            amount=json['amount'],
            currency=json['currency'],
        )

    @staticmethod
    def from_price_string(price_string, currency_hint = None):
        if type(price_string) is not str:
            price_string = str(price_string)

        if price_string is None or price_string == "":
            return None

        price = Price.fromstring(price_string, currency_hint=currency_hint)
        if price is None or price.amount is None:
            return None

        return GustmarketPrice(
            amount=price.amount_float,
            currency=price.currency,
        )
