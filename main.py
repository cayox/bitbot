import logging
from bitbot.strategy import *
from bitbot import BotManager, NAME
import sys
import getopt
import subprocess

logging.basicConfig(format='[%(asctime)s] [%(levelname)s]: %(message)s', level=logging.INFO)


HELP_STR = f"""
{'[-h, --help]':<24} this help page

{'[-c, --config]':<24} the config file you want to use 
{24*' '}     e.g.: -c "./myconfig.yml"

{'[-b, --bots]':<24} the bots from the config to start, seperated by ';'
{24*' '}     e.g.: -b "MyFavBot;My2ndFavBot"

{'[-t, --threaded]':<24} run the each bot in a seperate thread
"""


def main(argv: list[str]):
    print(NAME)

    config = r".\example_config.yml"
    bot_name = ""

    try:
        opts, _ = getopt.getopt(argv, "hc:b:",["help", "config=","bots="])
    except getopt.GetoptError as e:
        print(e)
        print(HELP_STR)
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(HELP_STR)
            sys.exit()
        elif opt in ("-c", "--config"):
            config = arg
        elif opt in ("-b", "--bots"):
            bot_name = arg
        
    bm = BotManager(config)
    
    if bot_name:
        bm.start_bot(bot_name)
        
        
        

    





if __name__ == "__main__":
    main(sys.argv[1:])
        