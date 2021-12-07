from bitbot.algorithm import TradingAlgorithmInterface
from bitbot import services
import datetime as dt
import logging

class TrendFollowing(TradingAlgorithmInterface):
    def generate_signal(self, open_position: bool = False) -> services.OrderDirection:
        lookback_time = dt.datetime.now() - dt.timedelta(seconds=self.config["lookback"])
        lookback = self.db[self.db["time"] >= lookback_time]
        rate = "bidRate" if open_position else "askRate"
        cumret = (lookback[rate].pct_change() + 1).cumprod() - 1

        if open_position:
            # buying
            if len(cumret) <= 1:
                return services.OrderDirection.NONE
            percentages = cumret[cumret.last_valid_index()]
            logging.info(f"{self.config['market']} change: {percentages} %")
            if percentages > self.config["buy_percentage"]:
                return services.OrderDirection.BUY
        else:          
            # selling
            data_since_buy = self.db[self.db["time"] > self.last_buy_time]
            if len(data_since_buy) <= 1:
                return services.OrderDirection.NONE
            
            since_buy_return = (data_since_buy[rate].pct_change() +1).cumprod()-1
            last_entry = since_buy_return[since_buy_return.last_valid_index()]
            logging.info(f"{self.config['market']} return since buy: {last_entry} %")
            if last_entry > self.config["sell_high"] or last_entry < self.config["sell_low"]:
                return services.OrderDirection.SELL

        return services.OrderDirection.NONE
        
        

        
