from bitbot.strategy import TradingStrategyInterface
import datetime as dt
from bitbot import services
import logging
import pandas as pd

class MacdRsiAlgorithm(TradingStrategyInterface):

    def generate_signal(self, candles: pd.DataFrame, log: callable) -> services.OrderDirection:
        last_valid_index = candles.last_valid_index()
        if last_valid_index is None:
            return services.OrderDirection.NONE
            
        rsi = candles.loc[last_valid_index, "rsi"]
        macd, signal, diff = candles.loc[last_valid_index, ["macd", "macd_signal", "macd_diff"]].to_list()

        log(f"## {self.market} ## RSI: {rsi:.2f} MACD: {macd:.2f} SIGNAL: {signal:.2f} DIFF: {diff:.2f}")
        if self.next_action == services.OrderDirection.BUY:
            # buying
            if rsi < self.trigger_params["rsi_buy"] and abs(diff) < self.trigger_params["macd_trigger_diff"] and \
                abs(macd) > self.trigger_params["macd_trigger_diff"] and abs(signal) > self.trigger_params["macd_trigger_diff"]:

                return services.OrderDirection.BUY
        else:
            # selling
            if rsi > self.trigger_params["rsi_sell"] and abs(diff) < self.trigger_params["macd_trigger_diff"] and \
                abs(macd) > self.trigger_params["macd_trigger_diff"] and abs(signal) > self.trigger_params["macd_trigger_diff"]:
                
                return services.OrderDirection.SELL
        return services.OrderDirection.NONE
