from src.utils import MovingAverage, RelativeStrengthIndex, TradingStrategy, CurrentPosition, StockOrder

class MACD(TradingStrategy):
    def __init__(
            self,
            macd_first_ma_day_count=12,  # default impl is 12 units of time
            macd_second_ma_day_count=26,  # default impl is 26 units of time
            signal_ma_day_count=9,  # default is 9 units of time
            momentum_ma_type='exponential',
            rsi_window=14,
            stop_loss_proportion=.01,
            profit_pull_proportion=.001
            # re-implement this as trailing stop proportion (so that rising profits keep rising)
    ):
        self.start_trading_day_count = max(macd_first_ma_day_count, macd_second_ma_day_count, rsi_window)
        self.macd_first_ma = MovingAverage(momentum_ma_type, macd_first_ma_day_count)
        self.macd_second_ma = MovingAverage(momentum_ma_type, macd_second_ma_day_count)
        self.signal_ma = MovingAverage(momentum_ma_type, signal_ma_day_count)
        self.macd_above_signal = None
        self.time_unit_count = 0
        self.rsi = RelativeStrengthIndex(rsi_window)
        self.stop_loss_proportion = stop_loss_proportion
        self.profit_pull_proportion = profit_pull_proportion

        if profit_pull_proportion < 0 or stop_loss_proportion < 0:
            raise Exception("The stop loss and/or profit pull proportions must be non-negative values")

    def execute(self, current_position, stock_data):
        # data is stock data and should have the format: open, high, low, close, volume
        # buy and sell orders will translate to buying and selling of the open price of the following day (unless changed)

        if not isinstance(current_position, CurrentPosition):
            raise TypeError("Object passed to the TradingStrategy inhereted object must be of type CurrentPosition")

        # update moving averages and rsi
        self.update_moving_averages(stock_data)
        self.time_unit_count += 1
        self.update_rsi(stock_data)

        # MACD business logic
        macd_line = self.macd_first_ma.ma_val - self.macd_second_ma.ma_val
        signal_line = self.signal_ma.ma_val

        longs_to_buy = 0
        longs_to_sell = 0
        shorts_to_buy = 0
        shorts_to_sell = 0

        if self.time_unit_count < self.start_trading_day_count:
            return StockOrder(longs_to_buy, longs_to_sell, shorts_to_buy, shorts_to_sell)

        if self.macd_above_signal is None:
            if macd_line > signal_line:
                self.macd_above_signal = True
            elif macd_line < signal_line:
                self.macd_above_signal = False

        elif self.macd_above_signal == True:
            # same as before, do nothing
            if macd_line > signal_line:
                self.macd_above_signal = True
            # crossover: macd cross above to below, indicates downward trend so sell longs (if possible) and sell shorts
            elif macd_line < signal_line:
                self.macd_above_signal = False
                longs_to_sell = current_position.longs_owned
                shorts_to_sell = round((current_position.capital / 2) / stock_data.last)

        elif self.macd_above_signal == False:
            # crossover: macd cross below to above, indicates upward trend so buy longs and buy shorts (if possible)
            if macd_line > signal_line:
                self.macd_above_signal = True
                shorts_to_buy = current_position.shorts_sold
                longs_to_buy = round((current_position.capital / 2) / stock_data.last)

            # same as before, do nothing
            elif macd_line < signal_line:
                self.macd_above_signal = False

        else:
            raise Exception(
                "macd_above_signal variable should only ever be True, False, or None. Investigate source code.")

        # put in stop loss and profit pull code here (check what gains/losses would be here if trading the close price)
        # approximates with the closing price of this time unit

        # stop loss and profit pull for shorts
        total_pnl = 0
        total_bet = 0
        total_shorts_sold = 0
        for key, value in current_position.shorts_sold_tracker.items():
            total_bet += key * value
            total_shorts_sold += value
            total_pnl += value * (key - stock_data.last)

        if total_bet != 0 and (total_pnl / total_bet) < -self.stop_loss_proportion:
            shorts_to_buy = total_shorts_sold
            shorts_to_sell = 0

        # TODO: implement trailing stop for profit pull to allow momentum to build
        if total_bet != 0 and (total_pnl / total_bet) > self.profit_pull_proportion:
            shorts_to_buy = total_shorts_sold
            shorts_to_sell = 0

        # stop loss and profit pull for longs
        total_pnl = 0
        total_bet = 0
        total_longs_bought = 0
        for key, value in current_position.longs_owned_tracker.items():
            total_bet += key * value
            total_longs_bought += value
            total_pnl += value * (stock_data.last - key)

        if total_bet != 0 and (total_pnl / total_bet) < -self.stop_loss_proportion:
            longs_to_sell = total_longs_bought
            longs_to_buy = 0

        # TODO: implement trailing stop for profit pull to allow momentum to build
        if total_bet != 0 and (total_pnl / total_bet) > self.profit_pull_proportion:
            longs_to_sell = total_longs_bought
            longs_to_buy = 0

        return StockOrder(longs_to_buy, longs_to_sell, shorts_to_buy, shorts_to_sell)

    def update_moving_averages(self, stock_data):
        # make the data point the average of the high and low
        data_point = stock_data.last
        datetime = stock_data.time_index

        self.macd_first_ma.update(data_point, datetime)
        self.macd_second_ma.update(data_point, datetime)
        self.signal_ma.update(self.macd_first_ma.ma_val - self.macd_second_ma.ma_val, datetime)

        return

    def update_rsi(self, stock_data):
        data_point = stock_data.last
        self.rsi.update_RSI(data_point)

        return
