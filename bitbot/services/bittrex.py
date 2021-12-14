import hashlib
import datetime as dt
import hmac
import json
import enum
from time import strftime
import requests
from bitbot import services
import pandas as pd

from bitbot.services.service import CandleInterval

BITTREX_URL = "https://api.bittrex.com/v3"


class BitTrex(services.ServiceInterface):
    def __init__(self):
        super().__init__("bittrex")

    def api_request(
        self,
        url: str,
        method: str = None,
        params: dict = None,
        body: dict[str, any] or str or list[any]  = None,
        headers: dict[str, str] = None):

        if not isinstance(body, str):
            body = json.dumps(body, separators=(',',':'))

        if method is None:
            method = "GET"

        # build full api uri
        if not url.startswith("http"):
            url = f"{BITTREX_URL}/{url[1:] if url.startswith('/') else url}"
        
        default_headers =  {
            "Content-Type": "application/json",
            "Api-Key": self._api_key,
            # UNIX timestamp, in epoch-millisecond format
            "Api-Timestamp": str(services.now_milliseconds()),
            "Api-Content-Hash": hashlib.sha512(body.encode("latin1") if body else "".encode()).hexdigest(),
        }


        # create request signature
        signature = [
            default_headers["Api-Timestamp"],
            url,
            str(method), 
            default_headers["Api-Content-Hash"]
            ]
        signature = "".join(signature)
        # encode signature
        sign = hmac.new(self._api_secret.encode(), signature.encode(), hashlib.sha512).hexdigest()

        default_headers["Api-Signature"] = sign

        # add custom headers
        if headers is not None:
            default_headers.update(headers)

        r = requests.request(method, url, params=params, data=body, headers=default_headers)

        if 200 <= r.status_code < 300:
            return r.json()
        raise Exception(f"Error {r.status_code}: {r.text}")
    
    #### Account

    def get_account_id(self) -> str:
        return self.api_request("/account")["accountId"]
    
    def get_available_balance(self, currency: str) -> float: 
        return float(self.api_request(f"/balances/{currency}")["available"])

    #### Markets
    
    def get_all_markets(self) -> dict[str, any]:
        return self.api_request(f"/markets")
    
    def get_market(self, market: str) -> dict[str, any]:
        return self.api_request(f"/markets/{market}")
    
    def get_market_summary(self, market: str) -> dict[str, any]:
        return self.api_request(f"/markets/{market}/summary")
    
    def get_market_ticker(self, market: str) -> dict[str, str]:
        return self.api_request(f"/markets/{market}/ticker")
    
    #### Orders
    
    def place_order(self, order: services.Order) -> list[dict[str, str]]:
        return self.api_request("/orders", "POST", body=str(order))
    
    #### candles

    def get_candles(self, market: str, candleinterval: services.CandleInterval) -> pd.DataFrame:
        response = self.api_request(f"/markets/{market}/candles/{candleinterval.value}/recent")
        # build dataframe
        df = pd.DataFrame(response, columns=list(response[0].keys()))

        # time conversion
        df["startsAt"] = pd.to_datetime(df["startsAt"], format="%Y-%m-%dT%H:%M:%SZ")
        # float conversion; values are strings by default
        for val in ["open", "close", "high", "low", "volume", "quoteVolume"]:
            df[val] = pd.to_numeric(df[val], downcast="float")
        return df
    
    def get_market_percentage(self, market: str, timedelta: dt.timedelta, calc_point: str = None) -> float:
        if calc_point is None:
            calc_point = "close"
        candle_interval = self.determine_candle_interval(timedelta)

        candles = self.get_candles(market, candle_interval)

        lookback = candles[candles["startsAt"] >= dt.datetime.utcnow() - timedelta]
        pcts = (lookback[calc_point].pct_change() + 1).cumprod() - 1
        if not len(pcts):
            return 0
        return pcts[pcts.last_valid_index()]
    
    def get_market_mean(self, market: str, timedelta: dt.timedelta, calc_point: str = None) -> float:
        if calc_point is None:
            calc_point = "close"
        candle_interval = self._determine_candle_interval(timedelta)

        candles = self.get_candles(market, candle_interval)

        lookback = candles[candles["startsAt"] >= dt.datetime.utcnow() - timedelta]
        if len(lookback) == 0:
            return 0
        return lookback[calc_point].mean()
            
            




if __name__ == "__main__":
    b = BitTrex()
    # print(b.get_percentage("close", "BTC-EUR", dt.timedelta(days=1)))
    print(b.get_market_ticker("BTC-EUR"))
    # o = services.Order("DFI-EUR", services.OrderDirection.BUY, services.OrderType.MARKET, services.TimeInForce.IMMEDIATE_OR_CANCEL, 2, use_awards=True)
    # print(b.place_order(o))