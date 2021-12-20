from bitbot import BotManager, NAME
import sys
import getopt
import subprocess


options = """
Options:

start [all | <BotName>]     Starts all or just a specific bot
quit                        Quits this application
change [cfg]                Change the config file

"""

def start_bot(bot_name: str):
    subprocess.Popen(f"start /wait python main.py -b {bot_name}", shell=True)

def main():

    print(NAME)

    user_input = input("What do you want to do? (type 'help' if you're new)\n>>> ")

    # TODO: implement settings manager
    bm = BotManager("example_config.yml")
    while True:
        args = user_input.strip().split(" ")
        cmd = args[0].lower()
        args = args[1:]

        if cmd == "start":
            if "all" in args:
                for bot_name in bm.bots:
                    start_bot(bot_name)
            else:
                for bot_name in args:
                    start_bot(bot_name)
        elif cmd == "help":
            print(options)
        elif cmd == "quit":
            print("Bye Bye")
            return
        else:
            print("Unknown command! Type 'help' for instructions")

        user_input = input(">>> ")
        
    

if __name__ == "__main__":
    main()