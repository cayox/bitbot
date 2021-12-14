from .strategy import TradingStrategyInterface
import datetime as dt


class MeanRevision(TradingStrategyInterface):


    def generate_signal(self):
        self.service.get_market_mean(self.config["market"], dt.timedelta(minutes=self.config["lookback"]))




