import json
from bitbot.algorithm import *
from bitbot.bot.bot import Bot
from bitbot.services import BitTrex
import datetime as dt


if __name__ == "__main__":
    b = BitTrex()
    pct = b.get_market_percentage("BTC-EUR", dt.timedelta(days=1))
    
    # print(pct)
    # print(b.get_available_balance("BTC"))
    with open(r"C:\Projects\bitbot\example_config.json") as f:
        json = json.load(f)
    b = Bot(json[0])
    b.start()
        