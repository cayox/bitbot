[![github pages](https://github.com/cayox/bitbot/actions/workflows/docs_deploy.yml/badge.svg?branch=main&event=push)](https://github.com/cayox/bitbot/actions/workflows/docs_deploy.yml)

# bitbot
Highly customizable trading bot 

# How to start

### 1. Download this repository
You can download this repository by cloning it via 

```bash
$ git clone https://github.com/cayox/bitbot.git
# or 
$ git clone git@github.com:cayox/bitbot.git
```

### 2. Install dependencies
You need Python >= `3.9` to run this application.

This project bases on some other Libraries. To install them you can:

```bash
$ cd bitbot
$ pip install -r requirements.txt
```

### 3. Start a bot
In the cloned folder, you can find two python files: `main.py` and `ìnterface.py`

#### main.py
The `main.py` file can be used to run a bot via regular commandline arguments. 

```bash
$ python main.py -c <path/to/config>.yml -b <botname>
```

This starts the bot with the name specified after `-b`. The name must be given in the config as typed.
If the config path is omitted, the `example_config.yml` in the root directory will be used.

#### interface.py
The `interface.py` file can be used to start an interactive "Control Center". From there, bots can be started and changes can be made. Each bot launches in a seperate terminal.

```bash
$ python interface.py
```

# Developer Info
If you're a developer and you want to contribute to this project, you can find the docs [here](https://cayox.github.io/bitbot/index.html)

Thank you for helping out!

