import pandas as pd
import pickle
import numpy as np

def process_raw_csv():
    data = pd.read_csv("data/data.csv")

    stocks = {}
    count = 0
    for i in data.index:
        if data.iloc[i]['ticker'] in stocks:
            stocks[data.iloc[i]['ticker']].loc[i] = data.iloc[i][['date', 'last', 'volume']]
        else:
            stocks[data.iloc[i]['ticker']] = pd.DataFrame(data.iloc[i][['date', 'last', 'volume']]).T
        count += 1

    for k in stocks.keys():
        stocks[k].reset_index().drop(columns='index')

    with open('data/stocks.pkl', 'wb') as f:
        pickle.dump(stocks, f)


# create more methods for adding in additional features (volume, MACD, moving averages, RSI, etc.)
# need to figure out how to get mismatching sample sizes to match up properly (might need to pass in labels here)
def generate_cnn_data_simple(data, window, labels):
    print(f"data shape at 0 {data.shape[0]}")
    print(f"length of the labels {len(labels)}")
    print(f"window size is {window}")

    max_lookback = max(data.shape[0] - len(labels), window)

    print(f"max lookback is {max_lookback}")
    samples = []

    for i in data.index:

        if i == data.shape[0] - max_lookback:
            break

        samples.append(np.array(data.iloc[i:i + window]['last']))

    print(f"length of the samples is {len(samples)}")
    print(f"length of the labels is {len(labels)}")

    # no matter what, you have to pull the difference in the amout of window and off the front of the labels to match up
    # only does anything if the window size exceed the label look ahead size

    if window > data.shape[0] - len(labels):
        labels = labels[window - (data.shape[0] - len(labels)):]

    print(f"length of the samples is {len(samples)}")
    print(f"length of the labels is {len(labels)}")

    return np.array(samples), np.array(labels)
