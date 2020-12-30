#!interpreter
# -*- coding: utf-8 -*-
# Configuration file 
import os
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
BINANCE_API_SOURCE_KEY = os.getenv("BINANCE_API_SOURCE_KEY")
BINANCE_API_SOURCE_SECRET = os.getenv("BINANCE_API_SOURCE_SECRET")

# Parameters for binance_data_extracion.py
# Beginning of the period to extract
START = "2019-12-24"

# End of the period to extact
END = "2020-12-24"

# Root path to save the data
PATH = "/Users/sebastientetaud/Documents/Python/trading/data/"
PATH_RESULT = "/Users/sebastientetaud/Documents/Python/trading/result/ma_strategy_sl_tp_1year_data/"
# candlestick parameters
KLINE = ['6h']
#KLINE = ['1d','12h','8h','6h','4h', '2h','1h','30m','15m','5m']

# Work with .../USDT pairs. e.g: BTCUSDT, ETHUSDT
PAIRS = "USDT"

AMOUNT = 100
FEES = 0.001
BACKTEST_PERIOD_IN_DAYS = 366

STOPLOSS = 0.03
TAKEPROFIT = 0.03