import json
import logging
import time
import datetime as dt
from bitbot import services, strategy, bot
import numpy as np


class BacktestBot(bot.Bot):
    """
    A bot that executes a certain strategy on history data

    Attributes:
        config (dict[str, any]): the loaded configuration
        next_action (services.OrderDirection): the next action; wether to sell or to buy
        history (pandas.DataFrame): a history of all transactions the bot has made

    Args:
        config (str or dict[str,any]): the configuration that the bot should use

    """    
    
    def run(self):
        """
        Method to start the Bot. Downloads history data in timeframe specified in the config file. Applies the ``generate_signal``
        method of the desired strategy. Outputs a Summary like so:

        ::


        Saves buying time, buying proceeds and order direction in an attribute called ``history``
        """
        # diable logging, because it slows down this fast process
        logger = logging.getLogger()
        logger.disabled = True
        
        # TODO: implement parameters from config file

        candles = self.service.get_history_data(self.config["market"], services.CandleInterval.MINUTE_1,
                                                dt.datetime.utcnow() - dt.timedelta(days=30), dt.datetime.utcnow())
        candles["rsi"] = self.strat.calc_rsi(candles)
        candles = self.strat.calc_macd(candles)
        candles = candles.reset_index()

        def apply_strat(index): 
            services.printProgressBar(index, len(candles.index), prefix=f"{'Applying strategy':<32}")
            return self.strat.generate_signal(candles.iloc[index-100:index]).value

        candles["order"] = candles.index.map(apply_strat)
        buys = candles[candles["order"] == "BUY"]
        sells = candles[candles["order"] == "SELL"]

        if len(buys) > len(sells):
            buys = buys.iloc[:-1]

        transactions = sells["open"].values - buys["open"].values
        profits = np.array([i for i in transactions if i > 0])
        losses = np.array([i for i in transactions if i <= 0])

        success_rate = len(losses)/len(profits)
        if success_rate >= 1:
            success_rate = -(len(profits)/len(losses))

        rel_win = transactions/buys["open"].values
        winning_rate = ((rel_win + 1).cumprod() -1)[-1]

        currency = self.config["market"].split("-")[1]

        print("\n\n\n### Summary ###\n\n"
              f"{'Transactions made:':<32}{len(transactions)}\n"
              "\n"
              f"{'Winning transactions:':<32}{len(profits)}\n"
              f"{'Total win:':<32}{profits.sum()}\n"
              f"{'Max win:':<32}{max(profits)} {currency}\n"
              f"{'Min win:':<32}{min(profits)} {currency}\n"
              f"{'Avg win:':<32}{profits.mean()} {currency}\n"
              "\n"
              f"{'Loosing transactions:':<32}{len(losses)}\n"
              f"{'Total loss:':<32}{losses.sum()}\n"
              f"{'Max loss:':<32}{min(losses)} {currency}\n"
              f"{'Min loss:':<32}{max(losses)} {currency}\n"
              f"{'Avg loss:':<32}{losses.mean()} {currency}\n"
              "\n"
              f"{'Success rate:':<32}{round(success_rate*100, 4)} %\n"
              f"{'Profit increase:':<32}{round(winning_rate*100, 4)} %\n"
              )

        logger.disabled = False

