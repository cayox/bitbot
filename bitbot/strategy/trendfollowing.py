from bitbot.strategy import TradingStrategyInterface
from bitbot import services
import datetime as dt
import logging
import pandas as pd


class TrendFollowing(TradingStrategyInterface):
    def generate_signal(self, candles: pd.DataFrame, log: callable) -> services.OrderDirection:
        last_valid_index = candles.last_valid_index()
        if last_valid_index is None:
            return services.OrderDirection.NONE

        roc = candles.loc[last_valid_index, "roc"]
        

        if self.next_action == services.OrderDirection.BUY:
            log(f"## {self.market} ## change: {roc*100} %")
            if roc > self.trigger_params["buy_percentage"]:
                self.buytime = candles.loc[last_valid_index, "startsat"]
                return services.OrderDirection.BUY
        else:          
            # selling
            candles_since_buy = self.calc_roc(candles.loc[candles["startsat"] > self.buytime].copy(), **self.config["ta_params"]["roc"])
            roc_since_buy = candles_since_buy.loc[candles_since_buy.last_valid_index(), "roc"]
            
            log(f"## {self.market} ## return since buy: {roc_since_buy*100} %")
            if roc_since_buy > self.trigger_params["sell_high"] or roc_since_buy < self.trigger_params["sell_low"]:
                return services.OrderDirection.SELL

        return services.OrderDirection.NONE
        
        

        
