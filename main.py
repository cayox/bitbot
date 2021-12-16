import json
import logging
from bitbot.strategy import *
from bitbot import BotManager
import datetime as dt
import yaml

logging.basicConfig(format='[%(asctime)s] [%(levelname)s]: %(message)s', level=logging.INFO)

if __name__ == "__main__":
    bm = BotManager(r"C:\Projects\bitbot\example_config.yml")
    bm.start_bot("Bot1")
        