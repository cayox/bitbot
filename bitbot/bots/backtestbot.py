import json
import logging
import time
import datetime as dt
from bitbot import services, strategy, bots
import numpy as np


class BacktestBot(bots.Bot):
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
        method of the desired strategy. Calculates wins and losses based on quantity given in template. Calculates values based on close.
        
        
        Outputs a Summary like so:

        ::

            ### Summary ###

            Transactions made:              11

            Winning transactions:           6
            Total win:                      13488.21875
            Max win:                        5240.8828125 EUR
            Min win:                        96.38671875 EUR
            Avg win:                        2248.036376953125 EUR

            Loosing transactions:           5
            Total loss:                     -1270.4921875
            Max loss:                       -713.265625 EUR
            Min loss:                       -63.25 EUR
            Avg loss:                       -254.0984344482422 EUR

            Success rate:                   54.5455 %
            Profit increase:                31.7619 %

  
        """
        # diable logging, because it slows down this fast process
        logger = logging.getLogger()
        logger.disabled = True

        backtest_cfg = self.config["backtest"]

        candles = self.service.get_history_data(self.config["market"], services.CandleInterval.MINUTE_1,
                                                backtest_cfg["start"], backtest_cfg["end"])
        candles = self.apply_tas(candles)
        candles = candles.reset_index()

        def apply_strat(index): 
            services.printProgressBar(index, len(candles.index), prefix=f"{'Applying strategy':<32}")
            return self.strat.generate_signal(candles.iloc[index-100:index], self.log).value

        candles["order"] = candles.index.map(apply_strat)
        buys = candles[candles["order"] == "BUY"]
        sells = candles[candles["order"] == "SELL"]

        if len(buys) == 0 or len(sells) == 0:
            print("\n\nNo transactions would have been made in this timeframe!")
            return

        if len(buys) > len(sells):
            buys = buys.iloc[:-1]

        qty = self.config["quantity"]

        transactions = (sells["close"].values * qty ) - (buys["close"].values * qty)
        profits = np.array([i for i in transactions if i > 0])
        losses = np.array([i for i in transactions if i <= 0])

        success_rate = len(profits)/len(transactions)

        rel_win = transactions/(buys["close"].values * qty)
        winning_rate = ((rel_win + 1).cumprod() -1)[-1]

        currency = self.config["market"].split("-")[1]

        print("")
        print(f"\n\n\n### Summary {self.name} ###\n\n"
              f"{'Timeframe:':<32}{backtest_cfg['start'].strftime('%Y-%m-%d %H:%M:%S') + ' - ' + backtest_cfg['end'].strftime('%Y-%m-%d %H:%M:%S')}\n"        
              "\n"    
              f"{'Transactions made:':<32}{len(transactions)}\n"
              "\n"
              f"{'Winning transactions:':<32}{len(profits)}\n"
              f"{'Total win:':<32}{profits.sum()} {currency}\n"
              f"{'Max win:':<32}{max(profits)} {currency}\n"
              f"{'Min win:':<32}{min(profits)} {currency}\n"
              f"{'Avg win:':<32}{profits.mean()} {currency}\n"
              "\n"
              f"{'Loosing transactions:':<32}{len(losses)}\n"
              f"{'Total loss:':<32}{losses.sum()} {currency}\n"
              f"{'Max loss:':<32}{min(losses)} {currency}\n"
              f"{'Min loss:':<32}{max(losses)} {currency}\n"
              f"{'Avg loss:':<32}{losses.mean()} {currency}\n"
              "\n"
              f"{'Est. input:':<32}{qty*candles['close'].iloc[0]} {currency}\n"
              f"{'Est. profit gain:':<32}{profits.sum() + losses.sum()} {currency}\n"
              f"{'Est. profit w/ holding:':<32}{(candles['close'].iloc[-1] - candles['close'].iloc[0]) * qty} {currency}\n"
              f"{'Total outcome:':<32}{(profits.sum() + losses.sum()) + (qty*candles['close'].iloc[0])} {currency}\n"
              "\n"
              f"{'Success rate:':<32}{round(success_rate*100, 4)} %\n"
              f"{'Profit increase:':<32}{round(winning_rate*100, 4)} %\n"
              )

        logger.disabled = False

