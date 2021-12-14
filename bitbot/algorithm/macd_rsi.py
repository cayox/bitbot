from .algorithm import TradingAlgorithmInterface
import datetime as dt
from bitbot import services
import logging

class MacdRsiAlgorithm(TradingAlgorithmInterface):

    def generate_signal(self, open_position: bool = False) -> services.OrderDirection:
        rsi = self.calc_recent_rsi()
        macd, signal, diff = self.calc_recent_macd()
        logging.info(f"## {self.config['market']} ## RSI: {rsi:.2f} MACD: {macd:.2f} SIGNAL: {signal:.2f} DIFF: {diff:.2f}")
        if open_position:
            # buying
            if rsi > self.strategy["rsi_buy"] and abs(diff) < self.strategy["macd_trigger_diff"] and \
                abs(macd) > self.strategy["macd_trigger_diff"] and abs(signal) > self.strategy["macd_trigger_diff"]:
                return services.OrderDirection.BUY
        else:
            # selling
            if rsi < self.strategy["rsi_sell"] and abs(diff) < self.strategy["macd_trigger_diff"] and \
                abs(macd) > self.strategy["macd_trigger_diff"] and abs(signal) > self.strategy["macd_trigger_diff"]:
                return services.OrderDirection.SELL
        return services.OrderDirection.NONE
