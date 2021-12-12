from abc import abstractmethod
import json
import time
import datetime as dt
from bitbot import services
import pandas as pd
import logging
from ta import momentum, trend

logging.basicConfig(format='[%(asctime)s] [%(levelname)s]: %(message)s', level=logging.INFO)


class TradingAlgorithmInterface:
    def __init__(self, portal: services.ServiceInterface, config: str or dict[str, any]):
        self.service = portal

        if isinstance(config, str):
            with open(config, encoding="utf8") as f:
                self.config = json.load(f)
        else:
            self.config = config
        
        self.strategy = self.config["strategy"]

        self.next_action = services.OrderDirection.BUY
        self.last_buy_time = None
        self.last_buy_value = 0
    
    def calc_recent_rsi(self) -> float:
        candles = self.service.get_candles(self.config["market"], services.CandleInterval.MINUTE_1)
        ind = momentum.RSIIndicator(candles["close"], window=self.config["rsi_window"])
        df_rsi = ind.rsi()
        return df_rsi[df_rsi.last_valid_index()]
    
    def calc_recent_macd(self) -> list[float]:
        candles = self.service.get_candles(self.config["market"], services.CandleInterval.MINUTE_1)
        obj = trend.MACD(candles["close"], self.config["macd_slow"], self.config["macd_fast"], self.config["macd_sign"])
        macd = obj.macd()
        signal = obj.macd_signal()
        histogram = obj.macd_diff()
        return [macd[macd.last_valid_index()], signal[signal.last_valid_index()], histogram[histogram.last_valid_index()]]


    def run(self):
        while True:
            available_balance = self.service.get_available_balance(self.config["market"].split("-")[0])
            signal = self.generate_signal(self.next_action == services.OrderDirection.BUY)
            if signal != services.OrderDirection.NONE:
                order = services.Order(self.config["market"], signal, services.OrderType.MARKET, 
                                           services.TimeInForce.IMMEDIATE_OR_CANCEL, 
                                           self.config["quantity"] if self.config["quantity"] <= available_balance else available_balance)

                try:
                    res = self.service.place_order(order)
                except Exception as e:
                    logging.error(f"{e}")
                    # TODO : remove raise
                    raise e
                    return
                
                if res["status"] != "CLOSED":
                    logging.warning(f'Could not place Order: Status: {res["status"]}')
                else:
                    logging.info(f'Placed Order: {res}')
                    self.next_action = services.OrderDirection.SELL if self.next_action == services.OrderDirection.BUY else services.OrderDirection.BUY
                    self.last_buy_time = dt.datetime.utcnow()
                    self.last_buy_value = res["proceeds"]


            time.sleep(self.config["update_interval"])

    @abstractmethod
    def generate_signal(self, buy_posotion: bool = False) -> services.OrderDirection:
        pass

    
    