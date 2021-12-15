import json
import logging
from bitbot.strategy import *
from bitbot.bot import Bot, BacktestBot
from bitbot.services import BitTrex
import datetime as dt

logging.basicConfig(format='[%(asctime)s] [%(levelname)s]: %(message)s', level=logging.INFO)

if __name__ == "__main__":
    b = BitTrex()
    pct = b.get_market_percentage("BTC-EUR", dt.timedelta(days=1))
    
    # print(pct)
    # print(b.get_available_balance("BTC"))
    with open(r"C:\Projects\bitbot\example_config.json") as f:
        json = json.load(f)
    b = BacktestBot(json[0])
    b.run()
        