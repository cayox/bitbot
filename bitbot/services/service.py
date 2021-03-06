from abc import abstractmethod
import json
import time
import sys
import datetime as dt
import enum
import pandas as pd


def now_milliseconds():
    return int(time.time() * 1000)

def date_time_milliseconds(date_time_obj):
    return int(time.mktime(date_time_obj.timetuple()) * 1000)    
    

class OrderDirection(enum.Enum):
    NONE = "NONE"
    SELL = "SELL"
    BUY = "BUY"

class TimeInForce(enum.Enum):
    GOOD_TIL_CANCELLED = "GOOD_TIL_CANCELLED"
    IMMEDIATE_OR_CANCEL = "IMMEDIATE_OR_CANCEL"
    FILL_OR_KILL = "FILL_OR_KILL"
    POST_ONLY_GOOD_TIL_CANCELLED = "POST_ONLY_GOOD_TIL_CANCELLED"
    BUY_NOW = "BUY_NOW"
    INSTANT = "INSTANT"

class CandleInterval(enum.Enum):
    MINUTE_1 = "MINUTE_1"
    MINUTE_5 = "MINUTE_5"
    HOUR_1 = "HOUR_1"
    DAY_1 = "DAY_1"

class OrderType(enum.Enum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"
    CEILING_LIMIT = "CEILING_LIMIT"
    CEILING_MARKET = "CEILING_MARKET"

class Order:
    def __init__(self, market: str, direction: OrderDirection, type: OrderType,
                    time_in_force: TimeInForce = None, quantity: float = 0, ceiling: float = 0, 
                    limit: float = 0, use_awards: bool = False) -> None:

        self.market = market
        self.direction = direction
        self.type = type
        self.quantity = quantity
        self.ceiling = ceiling
        self.limit = limit
        self.time_in_force = time_in_force if time_in_force is not None else TimeInForce.GOOD_TIL_CANCELLED
        self.use_awards = use_awards

    def __str__(self):
        out = {
                "marketSymbol": self.market,
                "direction": self.direction.value,
                "type": self.type.value,
                "timeInForce": self.time_in_force.value,
                "useAwards": str(self.use_awards).lower()
            }
        for item in ["ceiling", "quantity", "limit"]:
            val = getattr(self, item)
            if not val:
                continue
            out[item] = getattr(self, item)

        return str(out)

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 60, fill = '???', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    From: https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console

    Args:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * (filledLength) + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()


class ServiceInterface:
    def __init__(self, service_name: str = None):
        """
        Description of __init__

        Args:
            service_name (str=None): the name of the service. Used to get the secrets in the secrets file and to 
                find the right class to use

        """
        if service_name is None:
            return
            
        with open("./secrets.json", encoding="utf8") as f:
            self._config = json.load(f)[service_name]
            self._api_key = self._config["key"]
            self._api_secret = self._config["secret"]

    
    @staticmethod
    def determine_candle_interval(td: dt.timedelta) -> CandleInterval:
        DAY = dt.timedelta(days=1).total_seconds()
        secs = td.total_seconds()

        if 59 > secs > 366*DAY:
            raise ValueError("timdelta must be > 1 minute and < 366 days")

        if secs <= DAY:
            candleinterval = CandleInterval.MINUTE_1
        elif secs <= 31*DAY:
            candleinterval = CandleInterval.HOUR_1
        else:
            candleinterval = CandleInterval.DAY_1
        
        return candleinterval

    @abstractmethod
    def api_request(self, url: str, method: str = None, params: dict = None, body: dict or str = None, headers: dict[str, str] = None):
        pass

    @abstractmethod
    def get_available_balance(self, currency: str) -> float: 
        pass

    @abstractmethod
    def get_candles(self, market: str, candleinterval: CandleInterval) -> pd.DataFrame:
        pass

    @abstractmethod
    def get_market_ticker(self, market: str) -> dict[str, str]:
        pass

    @abstractmethod
    def get_market_percentage(self, market: str, timedelta: dt.timedelta, calc_point: str = None) -> float:
        pass

    @abstractmethod 
    def get_market_mean(self, market: str, timedelta: dt.timedelta, calc_point: str = None) -> float:
        pass

    @abstractmethod
    def get_market_ticker(self, market: str) -> dict[str, str]:
        pass

    @abstractmethod
    def place_order(self, orders: list[Order]) -> list[dict[str, str]]:
        pass
    
    @abstractmethod
    def get_history_data(self, market: str, candleinterval: CandleInterval, start: dt.datetime, end: dt.datetime) -> pd.DataFrame:
        pass