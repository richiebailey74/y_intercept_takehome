class RelativeStrengthIndex:
    def __init__(
            self,
            window=14
    ):
        self.window = window
        self.stock_vals = []
        self.price_diff_vals = []
        self.RSI = None
        self.filled_windows = False

    def update_RSI(self, data_point):
        if not self.filled_windows:
            self.stock_vals.append(data_point)
            if len(self.stock_vals) > 1:
                self.price_diff_vals.append(self.stock_vals[-1] - self.stock_vals[-2])
            if len(self.stock_vals) == 14:
                self.filled_windows = True

        else:
            self.stock_vals.append(data_point)
            self.price_diff_vals.append(self.stock_vals[-1] - self.stock_vals[-2])
            self.stock_vals.pop(0)
            self.price_diff_vals.pop(0)
            gains = [x for x in self.price_diff_vals if x > 0]
            losses = [-x for x in self.price_diff_vals if x < 0]
            if len(gains) == 0:
                self.RSI = 0
                return
            else:
                average_gain = sum(gains) / len(gains)

            if len(losses) == 0:
                self.RSI = 100
                return
            else:
                average_loss = sum(losses) / len(losses)

            if average_loss == 0 and average_gain == 0:
                self.RSI = 50
                return
            elif average_loss == 0:
                self.RSI = 100
                return
            else:
                self.RSI = 100 - (100 / (1 + (average_gain / average_loss)))

        return
