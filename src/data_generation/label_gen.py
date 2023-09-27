# further development: can maybe do a multilabel problem where the thresholds and distances are sepearated
# -based off of buying/selling shorts or longs and with separate proportions (or just buy vs sell)
def construct_threshold_distance_labels(data, thresh, dist):
    labels = []

    for i in data.index:

        if i + dist == data.shape[0]:
            break

        percent_change = (data.iloc[i + dist]['last'] - data.iloc[i]['last']) / data.iloc[i]['last']

        if percent_change > thresh:
            # buy
            labels.append(1)
        elif percent_change < -thresh:
            # sell
            labels.append(2)
        else:
            # hold
            labels.append(0)

    return labels


# ultra sensitive labels
# Going to construct labels such that any movement in the opposite direction constitutes a full swing on holdings
# theoretically shouldn't work that well since it is effectively learning the noise
def construct_sensitive_labels(data):
    # 0 is hold, 1 is buy long and buy short, 2 is sell long and sell short
    labels = []
    bought_longs = None
    sold_shorts = None
    if data.iloc[0]['last'] < data.iloc[1]['last']:
        labels.append(1)
        bought_longs = True
        sold_shorts = False
    else:
        labels.append(2)
        bought_longs = False
        sold_shorts = True

    for i in data.index:
        if i == 0:
            continue
        if i + 1 == data.shape[0]:
            break

        if data.iloc[i + 1]['last'] > data.iloc[i]['last']:
            # increased from the previous
            if sold_shorts:
                labels.append(1)
                bought_longs = True
                sold_shorts = False

        elif data.iloc[i + 1]['last'] < data.iloc[i]['last']:
            # decreased from the previous
            if bought_longs:
                labels.append(2)
                bought_longs = False
                sold_shorts = True

        else:
            # no change so hold
            labels.append(0)

    return labels


# future developments: can add an additional HP for vol thresh for buy and sell to be separate
def construct_moving_average_volume_labels(data, stma, ltma, vol_thresh):
    pass


# future developments: can add an additional HP for vol thresh for buy and sell to be separate
# can do so for deviation above and below for overbought and oversold thresholds
def construct_rsi_volume_labels(data, rsi_period, over_bs_deviation, vol_thresh):
    pass

