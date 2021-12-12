from bitbot.algorithm import TradingAlgorithmInterface
from bitbot import services
import datetime as dt
import logging


class TrendFollowing(TradingAlgorithmInterface):
    def generate_signal(self, open_position: bool = False) -> services.OrderDirection:
        if open_position:
            # buying
            pct_change = self.service.get_market_percentage(self.config["market"], dt.timedelta(minutes=self.strategy["lookback"]))

            logging.info(f"## {self.config['market']} ## change: {pct_change*100} %")
            if pct_change > self.strategy["buy_percentage"]:
                return services.OrderDirection.BUY
        else:          
            # selling
            pct_since_buy = self.service.get_market_percentage(self.config["market"], dt.datetime.utcnow() - self.last_buy_time)
            
            logging.info(f"## {self.config['market']} ## return since buy: {pct_since_buy*100} %")
            if pct_since_buy > self.strategy["sell_high"] or pct_since_buy < self.strategy["sell_low"]:
                return services.OrderDirection.SELL

        return services.OrderDirection.NONE
        
        

        
