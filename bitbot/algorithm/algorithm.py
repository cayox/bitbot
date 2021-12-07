from abc import abstractmethod
import json
import time
import datetime as dt
from bitbot import services
import pandas as pd
import logging

logging.basicConfig(format='[%(asctime)s] [%(levelname)s]: %(message)s', level=logging.INFO)


class TradingAlgorithmInterface:
    def __init__(self, portal: services.ServiceInterface, config: str or dict[str, any]):
        self.service = portal

        if isinstance(config, str):
            with open(config, encoding="utf8") as f:
                self.config = json.load(f)
        else:
            self.config = config
        
        self.db = pd.DataFrame()

        self.next_action = services.OrderDirection.BUY
        self.last_buy_time = None
        self.last_buy_value = 0
    
    def _fill_db(self):
        res = self.service.get_market_ticker(self.config["market"])
        res["time"] = dt.datetime.now()
        res["bidRate"] = float(res["bidRate"])
        res["askRate"] = float(res["askRate"])
        res["lastTradeRate"] = float(res["lastTradeRate"])
        self.db = self.db.append(res, ignore_index=True)

    def run(self):
        while True:
            self._fill_db()
            signal = self.generate_signal(self.next_action == services.OrderDirection.BUY)
            if signal is not services.OrderDirection.NONE:
                order = services.Order(self.config["market"], signal, services.OrderType.MARKET, 
                                           services.TimeInForce.IMMEDIATE_OR_CANCEL, self.config["quantity"])

                res = self.service.place_order(order)
                if res["status"] != "CLOSED":
                    logging.warning(f'Could not place Order: Status: {res["status"]}')
                else:
                    logging.info(f'Placed Order: {res}')
                    self.next_action = services.OrderDirection.SELL if self.next_action == services.OrderDirection.BUY else services.OrderDirection.BUY
                    self.last_buy_time = dt.datetime.now()
                    self.last_buy_value = res["proceeds"]
            time.sleep(self.config["update_interval"])

    @abstractmethod
    def generate_signal(self, open_position: bool = False) -> services.OrderDirection:
        pass

    
    