import sys
import json
from bitbot import services, algorithm

class Bot:
    def __init__(self, config: str or dict[str, any]):
        if isinstance(config, str):
            with open(config, encoding="utf8") as f:
                self.config = json.load(f)
        else:
            self.config = config

        
        self.service = getattr(services, self.config["service"])()
        self.algo = getattr(algorithm, self.config["algorithm"]["name"])(self.service, self.config["algorithm"])
    
    def start(self):
        self.algo.run()
