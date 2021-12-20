import hashlib
import datetime as dt
import hmac
import json
import logging
from os import terminal_size
import time
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
        df = df.rename({"startsAt": "time"})
        return df.rename(str.lower, axis='columns')
    
    #### market history
    
    def get_history_data(self, market: str, candleinterval: services.CandleInterval, start: dt.datetime, end: dt.datetime) -> pd.DataFrame:
        interval_days = 1
        if candleinterval == services.CandleInterval.HOUR_1:
            interval_days = 31
        elif candleinterval == services.CandleInterval.DAY_1:
            interval_days = 366


        if self.determine_candle_interval(end - start) == candleinterval:
            url = f"markets/{market}/candles/{candleinterval.value}/historical/{start.strftime('%Y')}/{start.strftime('%m')}/{start.strftime('%d')}"
            df = pd.DataFrame(self.api_request(url))
            df["startsAt"] = pd.to_datetime(df["startsAt"])
        else:
            next_start = start
            
            df = pd.DataFrame()

            max_iterations = int((end - start).days)
            i = 0
            services.printProgressBar(i, max_iterations, f"{'Downloading history':<32}")
            while next_start < end:
                url = f"markets/{market}/candles/{candleinterval.value}/historical/{next_start.strftime('%Y')}/{next_start.strftime('%m')}/{next_start.strftime('%d')}"
                new_df = pd.DataFrame(self.api_request(url))
                if new_df.empty:
                    print(f"\n### ERROR: Data in time {next_start.strftime('%Y-%m-%d %H:%M:%S') + ' - ' + (next_start + dt.timedelta(days=interval_days)).strftime('%Y-%m-%d %H:%M:%S')} not available")
                    return
                
                df = df.append(new_df, ignore_index=True)
                df["startsAt"] = pd.to_datetime(df["startsAt"], utc=True)
                next_start += dt.timedelta(days=interval_days)
                # to prevent to DOS the server, or get an error because too many requests
                # time.sleep(0.1)
                i += 1
                services.printProgressBar(i, max_iterations, f"{'Downloading history':<32}")
        
        df = df[df["startsAt"] < end.isoformat()]
        df = df.rename({"startsAt": "time"})
        # float conversion; values are strings by default
        for val in ["open", "close", "high", "low", "volume", "quoteVolume"]:
            df[val] = pd.to_numeric(df[val], downcast="float")
        return df.rename(str.lower, axis='columns')
            
            




if __name__ == "__main__":
    b = BitTrex()
    # print(b.get_percentage("close", "BTC-EUR", dt.timedelta(days=1)))
    print(b.get_market_ticker("BTC-EUR"))
    # o = services.Order("DFI-EUR", services.OrderDirection.BUY, services.OrderType.MARKET, services.TimeInForce.IMMEDIATE_OR_CANCEL, 2, use_awards=True)
    # print(b.place_order(o))