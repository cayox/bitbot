from bitbot.strategy import TradingStrategyInterface
from bitbot import services
import datetime as dt
import logging
import pandas as pd


class TrendFollowing(TradingStrategyInterface):
    def generate_signal(self, candles: pd.DataFrame, log: callable) -> services.OrderDirection:
        lookback = candles.iloc[-self.config["lookback"]:]
        pcts = (lookback["close"].pct_change() + 1).cumprod() - 1

        if self.next_action == services.OrderDirection.BUY:
            # buying
            pct_change = self.service.get_market_percentage(self.config["market"], dt.timedelta(minutes=self.trigger_params["lookback"]))

            log(f"## {self.market} ## change: {pct_change*100} %")
            if pct_change > self.trigger_params["buy_percentage"]:
                return services.OrderDirection.BUY
        else:          
            # selling
            pct_since_buy = self.service.get_market_percentage(self.config["market"], dt.datetime.utcnow() - self.last_buy_time)
            
            log(f"## {self.market} ## return since buy: {pct_since_buy*100} %")
            if pct_since_buy > self.trigger_params["sell_high"] or pct_since_buy < self.trigger_params["sell_low"]:
                return services.OrderDirection.SELL

        return services.OrderDirection.NONE
        
        

        
