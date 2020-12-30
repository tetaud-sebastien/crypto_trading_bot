#!interpreter
# -*- coding: utf-8 -*-
# Sebastien tetaud 2020-08-23
from binance.client import Client
from analytic_function import get_stock, telegram_send_message, no_connexion_message, check_order
import config
import time
import sys
import os
from datetime import datetime
import re


# Parameters
api_key_binance = config.api_key_binance
api_secret_binance = config.api_secret_binance
client = Client(api_key_binance, api_secret_binance)
path = config.PATH
list_KLINE = config.KLINE
start=config.START
end=config.END
pairs = config.PAIRS
start_datetime = datetime.strptime(start, '%Y-%m-%d')
end_datetime = datetime.strptime(end, '%Y-%m-%d')
period = end_datetime - start_datetime

# extract Binance symbols
info = client.get_exchange_info()
symbols = []
for i in info['symbols']:
    symbols.append(i['symbol'])

symbols = sorted(symbols)
print("Number of pairs %s" % len(symbols))
symbols = symbols

# extract pairs
list_pairs = []
for i in symbols:
    if re.search(pairs,i) :
        print(i)
        list_pairs.append(i)
list_pairs = sorted(list_pairs)

print("Number of %s pairs: %s" % (pairs , len(list_pairs)))



# Extract data 
# Loop for '1d','12h','8h','6h' candle ...
for kline in list_KLINE:
    
    path_foldername = os.path.join(path,kline)

    if not os.path.isdir(path_foldername):
        
        os.mkdir(path_foldername)
        print("Create %s repository" % path_foldername)
        
    # Loop for ETHUSDT BTCUSDT ....
    for SYMBOL in list_pairs:
        
        print('Extract: %s' % SYMBOL)
        # Extract data
        df = get_stock(symbol = SYMBOL, interval=kline,start=start,end=end, time_ref='Close_time')
        filename = os.path.join(path_foldername,SYMBOL)
        print(filename)
        df.to_csv(filename +'.xlsx')
