from abc import abstractmethod
import json
from bitbot import services
import logging
from ta import momentum, trend

logging.basicConfig(format='[%(asctime)s] [%(levelname)s]: %(message)s', level=logging.INFO)


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
    
    def calc_recent_rsi(self) -> float:
        """
        Method to calulate the RSI of the most recent data. uses ``rsi_window`` from the config as windowsetting.
        Always uses "close" value of candles.

        Returns:
            float

        """
        candles = self.service.get_candles(self.market, services.CandleInterval.MINUTE_1)
        ind = momentum.RSIIndicator(candles["close"], window=self.config["rsi_window"])
        df_rsi = ind.rsi()
        return df_rsi[df_rsi.last_valid_index()]
    
    def calc_recent_macd(self) -> list[float]:
        """
        Method to calulate the RSI of the most recent data. uses ``macd_slow``, ``macd_fast`` and ``macd_sign`` from the config as paraeters
        Always uses "close" value of candles.

        Returns:
            float

        """
        candles = self.service.get_candles(self.market, services.CandleInterval.MINUTE_1)
        obj = trend.MACD(candles["close"], self.config["macd_slow"], self.config["macd_fast"], self.config["macd_sign"])
        macd = obj.macd()
        signal = obj.macd_signal()
        histogram = obj.macd_diff()
        return [macd[macd.last_valid_index()], signal[signal.last_valid_index()], histogram[histogram.last_valid_index()]]

    @abstractmethod
    def generate_signal(self, buy_position: bool = False) -> services.OrderDirection:
        """
        Method to generate a buying or selling signal based on any market data

        Args:
            buy_position (bool=False): Wether function should check for buying or selling conditions

        Returns:
            services.OrderDirection

        """
        pass

    
    