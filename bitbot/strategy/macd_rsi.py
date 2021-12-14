from bitbot.strategy import TradingStrategyInterface
import datetime as dt
from bitbot import services
import logging

class MacdRsiAlgorithm(TradingStrategyInterface):

    def generate_signal(self, open_position: bool = False) -> services.OrderDirection:
        rsi = self.calc_recent_rsi()
        macd, signal, diff = self.calc_recent_macd()
        logging.info(f"## {self.market} ## RSI: {rsi:.2f} MACD: {macd:.2f} SIGNAL: {signal:.2f} DIFF: {diff:.2f}")
        if open_position:
            # buying
            if rsi > self.trigger_params["rsi_buy"] and abs(diff) < self.trigger_params["macd_trigger_diff"] and \
                abs(macd) > self.trigger_params["macd_trigger_diff"] and abs(signal) > self.trigger_params["macd_trigger_diff"]:
                return services.OrderDirection.BUY
        else:
            # selling
            if rsi < self.trigger_params["rsi_sell"] and abs(diff) < self.trigger_params["macd_trigger_diff"] and \
                abs(macd) > self.trigger_params["macd_trigger_diff"] and abs(signal) > self.trigger_params["macd_trigger_diff"]:
                return services.OrderDirection.SELL
        return services.OrderDirection.NONE
