class TradingStrategy:
    def execute(self, data):
        raise NotImplementedError(
            "The base class cannot be used, a particular trading strategy must implement this class!")


class CurrentPosition:
    def __init__(self, longs_owned, shorts_sold, capital):
        self.longs_owned = longs_owned
        self.shorts_sold = shorts_sold
        self.capital = capital

        # the keys will be the price and the values will the number bought (will help for more complex implementations)
        self.longs_owned_tracker = {}
        self.shorts_sold_tracker = {}


class StockOrder:
    def __init__(self, longs_to_buy, longs_to_sell, shorts_to_buy, shorts_to_sell):
        self.longs_to_buy = longs_to_buy
        self.longs_to_sell = longs_to_sell
        self.shorts_to_buy = shorts_to_buy
        self.shorts_to_sell = shorts_to_sell
