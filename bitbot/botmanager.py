import logging
from bitbot import bots
import yaml


class BotManager:
    def __init__(self, fp: str):

        with open(fp, "r") as stream:
            self.config = yaml.safe_load(stream)
        
        self.bots = {}
        
        for name, cfg in self.config.items():
            # initialize service class from imports
            bot_cls : bots.Bot = getattr(bots, cfg["type"])
            bot = bot_cls(name, cfg)

            self.bots[name] = bot
    
    def run_all(self):
        for name in self.bots:
            self.start_bot(name)
    
    def start_bot(self, name: str):
        if name not in self.bots:
            raise ValueError(f"{name} not defined in config")

        logging.info(f"Starting {name} Bot ...")
        self.bots[name].run()

        