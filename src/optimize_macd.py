from src.backtest import Backtester
from src.trading_strategies import MACD
import pickle

# hypertune MACD parameters for a given stock
def tune_MACD(data):
    momentum_types = ['exponential', 'simple']
    macd_first = [8, 12, 17]
    macd_second = [19, 26, 39]
    signals = [7, 9, 14]
    rsi_window = [9, 14, 20]
    stops = [.001, .01]
    pulls = stops = [.001, .01]

    max_gain = 0
    optimal_params = None

    for mt in momentum_types:
        for mf in macd_first:
            for ms in macd_second:
                for si in signals:
                    for rw in rsi_window:
                        for st in stops:
                            for pu in pulls:

                                bt = Backtester(MACD(mf, ms, si, mt, rw, st, pu), data, 1000000)
                                relative_gain, volatility = bt.backtest()

                                if relative_gain > max_gain:
                                    max_gain = relative_gain
                                    optimal_params = (mf, ms, si, mt, rw, st, pu)

    return max_gain, optimal_params


gains = []
vols = []
optimal_params = {}
gains = {}

with open('data/stocks.pkl', 'rb') as f:
    stocks = pickle.load(f)

for k in stocks.keys():
    mg, op = tune_MACD(stocks[k])
    optimal_params[k] = op
    gains[k] = mg

with open('data/optimal_params.pkl', 'wb') as f:
    pickle.dump(optimal_params, f)


