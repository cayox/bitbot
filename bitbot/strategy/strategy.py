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
    
    def calc_rsi(self, candles: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """
        Method to calulate the rsi of the specified data. Accepts the same parameter as in :ref:`ta.momentum.RSIIndicator<https://technical-analysis-library-in-python.readthedocs.io/en/latest/ta.html#ta.momentum.RSIIndicator>`

        
        Args:
            candles (pd.Dataframe): the Dataframe to which the rsi should be applied to

        Returns:
            pd.DataFrame: returns the same dataframe with a ``"rsi"`` column

        """
        ind = momentum.RSIIndicator(candles["close"], **kwargs)
        candles["rsi"] = ind.rsi()

        return candles
    
    def calc_macd(self, candles: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """
        Method to calulate the macd of the most recent data. Accepts the same parameter as in :ref:`ta.trend.MACD<https://technical-analysis-library-in-python.readthedocs.io/en/latest/ta.html#ta.trend.MACD>`

        Args:
            candles (pd.Dataframe): the Dataframe to which the macd should be applied to

        Returns:
            pd.DataFrame: returns the same dataframe with ``"macd"``, ``"macd_signal"`` and ``"macd_diff"`` columns

        """
        obj = trend.MACD(candles["close"], **kwargs)
        candles.loc[:, "macd"] = obj.macd()
        candles.loc[:, "macd_signal"] = obj.macd_signal()
        candles.loc[:, "macd_diff"] = obj.macd_diff()
        return candles
        
    @abstractmethod
    def generate_signal(self, candles: pd.DataFrame, log: callable) -> services.OrderDirection:
        """
        Method to generate a buying or selling signal based on any market data. Must be overwritten from specific or self implemented Strategies.

        Args:
            buy_position (bool=False): Wether method should check for buying or selling conditions

        Returns:
            services.OrderDirection

        """
        pass

    
    