import pickle
from src.trading_strategies import MACD
from src.backtest import Backtester

with open('data/optimal_params.pkl', 'rb') as f:
    optimal_params = pickle.load(f)

with open('data/stocks.pkl', 'rb') as f:
    stocks = pickle.load(f)

for k in stocks.keys():
    mf, ms, si, mt, rw, st, pu = optimal_params[k]
    bt = Backtester(MACD(mf, ms, si, mt, rw, st, pu), stocks[k], 1000000)
    bt.backtest(verbose=True)
