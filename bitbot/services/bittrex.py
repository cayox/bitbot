import hashlib
import datetime as dt
import hmac
import json
import enum
import requests
from bitbot import services

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
    
    def get_balance(self, currency: str) -> dict[str, any]: 
        return self.api_request(f"/balances/{currency}")

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

    def get_candles(self, market: str, candleinterval: services.CandleInterval) -> dict[str, str]:
        return self.api_request(f"/markets/{market}/candles/{candleinterval.name}/recent")
    
    def get_avg(self, calc_point: str, market: str, timedelta: dt.timedelta) -> float:
        days = timedelta.days
        current_date = dt.datetime.now()

        if days < 0:
            raise ValueError("startdate must be before current datetime")

        if days <= 1:
            candleinterval = services.CandleInterval.MINUTE_1
        elif days <= 31:
            candleinterval = services.CandleInterval.HOUR_1
        else:
            candleinterval = services.CandleInterval.DAY_1

        response = self.get_candles(market, candleinterval)
        sum = 0
        amount = 0 
        for item in response:
            if dt.datetime.strptime(item["startsAt"], "%Y-%m-%dT%H:%M:%SZ") < current_date - timedelta:
                continue

            sum += float(item[calc_point])
            amount += 1
        return sum/amount
    
    def get_percentage(self, calc_point: str, market: str, timedelta: dt.timedelta) -> float:
        days = timedelta.days
        current_date = dt.datetime.now()

        if days < 0:
            raise ValueError("startdate must be before current datetime")

        if days <= 1:
            candleinterval = services.CandleInterval.MINUTE_1
        elif days <= 31:
            candleinterval = services.CandleInterval.HOUR_1
        else:
            candleinterval = services.CandleInterval.DAY_1

        response = self.get_candles(market, candleinterval)
        for item in response:
            if dt.datetime.strptime(item["startsAt"], "%Y-%m-%dT%H:%M:%SZ") < current_date - timedelta:
                continue
            return 1 - (float(item[calc_point])/float(response[-1][calc_point]))
        return 0
            
            




if __name__ == "__main__":
    b = BitTrex()
    # print(b.get_percentage("close", "BTC-EUR", dt.timedelta(days=1)))
    print(b.get_market_ticker("BTC-EUR"))
    o = services.Order("DFI-EUR", services.OrderDirection.BUY, services.OrderType.MARKET, services.TimeInForce.IMMEDIATE_OR_CANCEL, 2, use_awards=True)
    print(b.place_order(o))