from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, MaxPooling1D, Flatten, Dense
from tensorflow.keras.utils import to_categorical
import tensorflow as tf
from tensorflow.keras.optimizers import Nadam
from src.utils import TradingStrategy, CurrentPosition, StockOrder
from sklearn.preprocessing import MinMaxScaler
import numpy as np


class CNN(TradingStrategy):
    def __init__(
            self,
            stop_loss_proportion=.02,
            profit_pull_proportion=.02
            # re-implement this as trailing stop proportion (so that rising profits keep rising)
    ):
        self.stop_loss_proportion = stop_loss_proportion
        self.profit_pull_proportion = profit_pull_proportion
        self.cnn_model = None
        self.previous_point = None
        self.scaler = None

        if profit_pull_proportion < 0 or stop_loss_proportion < 0:
            raise Exception("The stop loss and/or profit pull proportions must be non-negative values")

    def train_model(self, X_train, y_train):

        self.scaler = MinMaxScaler()
        self.scaler.fit(X_train)
        X_train_trans = self.scaler.transform(X_train)

        y_train = to_categorical(y_train, num_classes=len(np.unique(y_train)))

        model = Sequential()
        model.add(Conv1D(filters=16, kernel_size=2, activation='relu', input_shape=(X_train.shape[1], 1)))
        model.add(Conv1D(filters=16, kernel_size=2, activation='relu'))
        model.add(MaxPooling1D(pool_size=2))
        model.add(Conv1D(filters=32, kernel_size=3, activation='relu', input_shape=(X_train.shape[1], 1)))
        model.add(Conv1D(filters=32, kernel_size=3, activation='relu'))
        model.add(MaxPooling1D(pool_size=3))
        model.add(Flatten())
        model.add(Dense(16, activation='relu'))
        model.add(Dense(8, activation='relu'))
        model.add(Dense(y_train.shape[1], activation='softmax',
                        bias_initializer=keras.initializers.RandomNormal(stddev=np.sqrt(0.1)),
                        kernel_initializer=keras.initializers.Zeros(), use_bias=False))
        optimizer = Nadam(learning_rate=.001)
        model.compile(optimizer=optimizer, loss='categorical_crossentropy', metrics=['accuracy'])
        model.summary()

        history = model.fit(X_train_trans.astype('float32'), y_train.astype('int32'), epochs=1000, batch_size=128,
                            validation_split=0.2)
        self.cnn_model = model
        self.previous_point = X_train[-1:]
        return

    def execute(self, current_position, stock_data):
        # data is stock data and should have the format: date, last, volume
        # buy and sell orders will translate to buying and selling of the current day

        if self.cnn_model is None:
            raise Exception("Must first train the CNN architecture first in order to be able to predict signal")

        if not isinstance(current_position, CurrentPosition):
            raise TypeError("Object passed to the TradingStrategy inhereted object must be of type CurrentPosition")

        longs_to_buy = 0
        longs_to_sell = 0
        shorts_to_buy = 0
        shorts_to_sell = 0

        # construct valid data point and put into tracker for next data point
        self.previous_point = np.roll(self.previous_point, -1)
        self.previous_point[-1] = stock_data.last
        to_predict = self.scaler.transform(self.previous_point[-1].reshape(1, -1))

        # perform prediction and get argmax to get the label from the softmax layer
        action = np.argmax(self.cnn_model.predict(to_predict.reshape(1, -1).astype('float32')))
        # action is 0 for hold, 1 for buy, and 2 for sell
        print(f"action is {action}")
        # buying back all shorts at a profit
        # selling all longs at a profit
        # it is a risk adverse strategy - should put in trailing losses for each to maximize profits
        # could make buy and sell proportions a hyperparameter
        if action == 1:
            shorts_to_sell = current_position.shorts_sold
            longs_to_buy = round((current_position.capital / 10) / stock_data.last)

        elif action == 2:
            longs_to_sell = current_position.longs_owned
            shorts_to_buy = round((current_position.capital / 10) / stock_data.last)

        elif action == 0:
            pass  # do nothing / hold
        else:
            raise Exception("Invalid action received from model")

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
