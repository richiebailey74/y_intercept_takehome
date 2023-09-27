from src.utils import CurrentPosition, StockOrder, StockData
import matplotlib.pyplot as plt
import numpy as np

class Backtester:
    def __init__(self, strategy, data, initial_capital):
        self.strategy = strategy
        self.data = data.copy()
        self.initial_capital = initial_capital
        self.longs_profits_and_losses = []
        self.shorts_profits_and_losses = []
        self.results = None
        self.current_position = CurrentPosition(0, 0, initial_capital)

    def backtest(self, verbose=False):

        for ind in self.data.index:
            temp_data = self.data.loc[ind]
            stock_data = StockData(temp_data['last'], temp_data['volume'], temp_data['date'])
            stock_order = self.strategy.execute(self.current_position, stock_data)
            self.update_position(stock_data.last, stock_order, self.current_position)

        capital_in_assets = 0
        for key, value in self.current_position.longs_owned_tracker.items():
            capital_in_assets += key * value

        for key, value in self.current_position.shorts_sold_tracker.items():
            capital_in_assets += key * value

        if verbose:
            print(f"\nLiquid capital: ${self.current_position.capital}")
            print(f"Capital in assets: ${capital_in_assets}")
            print(f"Total capital: ${self.current_position.capital + capital_in_assets}")
            print(
                f"Relative gain or loss: {(self.current_position.capital + capital_in_assets) / self.initial_capital}")

            # plt.plot(list(range(len(self.longs_profits_and_losses))), self.longs_profits_and_losses)
            # plt.plot(list(range(len(self.shorts_profits_and_losses))), self.shorts_profits_and_losses)
            # plt.legend(['longs', 'shorts'])
            # plt.show()

        # returnn the relative gain to the initial capital, as well as annualized volatility
        return (self.current_position.capital + capital_in_assets) / self.initial_capital, self.data[
            'last'].std() * np.sqrt(252)

    def update_position(self, stock_val, order, position):

        if not isinstance(order, StockOrder):
            raise TypeError("Object passed to the Backtester object must be of type StockOrder")

        if not isinstance(position, CurrentPosition):
            raise TypeError(
                "Fundamental issue with backtester, current position not in correct format, investigate source code")

        # order to buy a long: take money out of the capital of current position and credit longs to current position
        if order.longs_to_buy > 0:
            position.longs_owned += order.longs_to_buy
            position.capital -= stock_val * order.longs_to_buy
            if stock_val not in position.longs_owned_tracker:
                position.longs_owned_tracker[stock_val] = order.longs_to_buy
            else:
                position.longs_owned_tracker[stock_val] += order.longs_to_buy

        # order to sell a long: remove longs from current position and credit capital to current position
        if order.longs_to_sell > 0:
            position.longs_owned -= order.longs_to_sell
            position.capital += stock_val * order.longs_to_sell
            to_sell = order.longs_to_sell
            to_del = []
            for key, value in position.longs_owned_tracker.items():
                if value == to_sell:
                    self.longs_profits_and_losses.append(to_sell * (stock_val - key))
                    to_del.append(key)
                    break
                elif value > to_sell:
                    self.longs_profits_and_losses.append(to_sell * (stock_val - key))
                    position.longs_owned_tracker[key] = value - to_sell
                    break
                elif value < to_sell:
                    self.longs_profits_and_losses.append(to_sell * (stock_val - key))
                    to_del.append(key)

            for d in to_del:
                del position.longs_owned_tracker[d]

        # order to buy a short: remove shorts sold to current position and take money out of capital of current position
        if order.shorts_to_buy > 0:
            position.shorts_sold -= order.shorts_to_buy
            position.capital -= stock_val * order.shorts_to_buy
            to_buy = order.shorts_to_buy
            to_del = []
            for key, value in position.shorts_sold_tracker.items():
                if value == to_buy:
                    self.shorts_profits_and_losses.append(to_buy * (key - stock_val))
                    to_del.append(key)
                    break
                elif value > to_buy:
                    self.shorts_profits_and_losses.append(to_buy * (key - stock_val))
                    position.shorts_sold_tracker[key] = value - to_buy
                    break
                elif value < to_buy:
                    self.shorts_profits_and_losses.append(to_buy * (key - stock_val))
                    to_del.append(key)

            for d in to_del:
                del position.shorts_sold_tracker[d]

        # order to sell a short: add shorts sold to current position and credit capital to current position
        if order.shorts_to_sell > 0:
            position.shorts_sold += order.shorts_to_sell
            position.capital += stock_val * order.shorts_to_sell
            if stock_val not in position.shorts_sold_tracker:
                position.shorts_sold_tracker[stock_val] = order.shorts_to_sell
            else:
                position.shorts_sold_tracker[stock_val] += order.shorts_to_sell
