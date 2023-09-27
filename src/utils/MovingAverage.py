class MovingAverage:
    def __init__(
            self,
            ma_type,  # will be exponential or simple
            window
    ):
        self.ma_type = ma_type
        self.window = window
        self.point_count = 0
        self.break_window = False
        self.sum = 0
        self.ma_val = None
        self.multiplier = 1  # average number of samples per day (introduce func to take the time unit type to adjust multiplier)
        self.alpha = 2 / (self.multiplier * window + 1)
        self.vals = []

    def update(self, data_point, datetime):
        # for simple or if there aren't enough points for exponential yet
        if self.ma_type == 'simple' or not self.break_window:
            self.sum += data_point
            if not self.break_window:
                self.point_count += 1
                self.vals.append(data_point)
            else:
                self.sum -= self.vals[0]
                self.vals.pop(0)
                self.vals.append(data_point)

            self.ma_val = self.sum / self.point_count

            if self.point_count == self.multiplier * self.window:
                self.break_window = True

        elif self.ma_type == 'exponential':
            # built in recursive nature makes it so the (1 - alpha) is applied to the entire suite of older points
            self.ma_val = (data_point - self.ma_val) * self.alpha + self.ma_val

        else:
            print(f"Invalid moving average type: {self.ma_type}")

        return
