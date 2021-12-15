from abc import abstractmethod
import json
from bitbot import services
from ta import momentum, trend
import pandas as pd


class TradingStrategyInterface:
    """
    Description of TradingStrategyInterface

    Attributes:
        service (services.ServiceInterface): the service to be used for requests
        config (dict[str, any]): the strategy configuration
        market (str):
        trigger_params (dict[str, any]): the parameter used to trigger a sell or buy order

    Args:
        service (services.ServiceInterface): the service to be used for requests
        config (str or dict[str,any]): the strategy configuration
        market (str): the market name, e.g.: ``"BTC-USD"``

    """
    def __init__(self, service: services.ServiceInterface, config: str or dict[str, any], market: str):
        self.service = service

        if isinstance(config, str):
            with open(config, encoding="utf8") as f:
                self.config = json.load(f)
        else:
            self.config = config

        
        self.market = market        
        self.trigger_params = self.config["trigger_params"]
         
        self.next_action = services.OrderDirection.BUY
    
    def calc_rsi(self, candles: pd.DataFrame) -> pd.DataFrame:
        """
        Method to calulate the RSI of the most recent data. uses ``rsi_window`` from the config as windowsetting.
        Always uses "close" value of candles.

        Returns:
            float

        """
        ind = momentum.RSIIndicator(candles["close"], window=self.config["rsi_window"])
        df_rsi = ind.rsi()
        return df_rsi
    
    def calc_macd(self, candles: pd.DataFrame) -> list[float]:
        """
        Method to calulate the RSI of the most recent data. uses ``macd_slow``, ``macd_fast`` and ``macd_sign`` from the config as paraeters
        Always uses "close" value of candles.

        Returns:
            float

        """
        obj = trend.MACD(candles["close"], self.config["macd_slow"], self.config["macd_fast"], self.config["macd_sign"])
        candles["macd"] = obj.macd()
        candles["macd_signal"] = obj.macd_signal()
        candles["macd_diff"] = obj.macd_diff()
        return candles
        
    @abstractmethod
    def generate_signal(self, candles: pd.DataFrame) -> services.OrderDirection:
        """
        Method to generate a buying or selling signal based on any market data. Must be overwritten from specific or self implemented Strategies.

        Args:
            buy_position (bool=False): Wether method should check for buying or selling conditions

        Returns:
            services.OrderDirection

        """
        pass

    
    