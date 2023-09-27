class FinancialInstrumentData:
    def getData(self):
        raise NotImplementedError(
            "The base class cannot be used, a particular security or derivative type must implement this class!")


class StockData(FinancialInstrumentData):

    def __init__(self, last, volume, time_index):
        self.last = last
        self.volume = volume
        self.time_index = time_index

    def getData(self):
        return self.last, self.volume, self.time_index
