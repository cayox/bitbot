from abc import abstractmethod
import json
import time
import datetime as dt
import enum


def now_milliseconds():
    return int(time.time() * 1000)

def date_time_milliseconds(date_time_obj):
    return int(time.mktime(date_time_obj.timetuple()) * 1000)    
    

class OrderDirection(enum.Enum):
    NONE = 0
    SELL = 1
    BUY = 2

class TimeInForce(enum.Enum):
    GOOD_TIL_CANCELLED = 0
    IMMEDIATE_OR_CANCEL = 1
    FILL_OR_KILL = 2
    POST_ONLY_GOOD_TIL_CANCELLED = 3
    BUY_NOW = 4
    INSTANT = 5

class CandleInterval(enum.Enum):
    MINUTE_1 = 0
    MINUTE_5 = 1
    HOUR_1 = 2
    DAY_1 = 3

class OrderType(enum.Enum):
    LIMIT = 0
    MARKET = 1
    CEILING_LIMIT = 2
    CEILING_MARKET = 3

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
                "direction": self.direction.name,
                "type": self.type.name,
                "timeInForce": self.time_in_force.name,
                "useAwards": str(self.use_awards).lower()
            }
        for item in ["ceiling", "quantity", "limit"]:
            val = getattr(self, item)
            if not val:
                continue
            out[item] = getattr(self, item)

        return str(out)


class ServiceInterface:
    def __init__(self, service_name: str):
        with open("./secrets.json", encoding="utf8") as f:
            self._config = json.load(f)[service_name]
        self._api_key = self._config["key"]
        self._api_secret = self._config["secret"]

    @abstractmethod
    def api_request(self, url: str, method: str = None, params: dict = None, body: dict or str = None, headers: dict[str, str] = None):
        pass

    @abstractmethod
    def get_percentage(self, calc_point: str, market: str, timedelta: dt.timedelta) -> float:
        pass

    @abstractmethod
    def get_market_ticker(self, market: str) -> dict[str, str]:
        pass

    @abstractmethod
    def place_order(self, orders: list[Order]) -> list[dict[str, str]]:
        pass