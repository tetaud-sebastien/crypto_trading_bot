#!interpreter
# -*- coding: utf-8 -*-
# Sebastien tetaud 2020-08-23
# Trading with EMA indicator, SL, TP, and cumulative capital.
# EMA/TP/SL has been optimized for the previous with the following characterics:
# EMA fast period = 7
# EMA slow period = 19 
# Stop Loss 8%
# Take Profit 3% 
# Candle 6h 
# ---------------- #
# BackTest results:
# Performance: 165.37
# Stop Loss:  0.08
# Take Profit: 0.03
# Fast EMA:  7
# Slow EMA: 19
# Profit Factor: 3.1
# ---------------- #
from binance.client import Client
from function import get_stock_bot, telegram_send_message, check_order
import config
import time
import sys
from datetime import datetime, timedelta
import json

# import config for Telegram
my_token = config.TELEGRAM_TOKEN
chat_id= config.TELEGRAM_CHAT_ID
# import config for Binance 
binance_api_source_key = config.BINANCE_API_SOURCE_KEY
binance_api_sources_secret = config.BINANCE_API_SOURCE_SECRET

# import config variable
symbol = config.SYMBOL
amount = config.AMOUNT
kline = config.KLINE
stopLoss = config.STOPLOSS
takeProfit = config.TAKEPROFIT

client = Client(binance_api_source_key, binance_api_sources_secret)

# Parameters
longState = True
shortState = False
buyStatus = False
buyPrice = 0
priceStopLoss = 0
priceTakeProfit = 0

if __name__ == "__main__":
    
    while True:

        with open('src/bot_status.json') as json_file:
            status = json.load(json_file)

        if status['status'] == 'start':
            # Get data
            try: 
                
                data = get_stock_bot(symbol, kline, "9 days ago UTC", 'Close_time')
                # calcultate the EMA slow and fast  + round to 4 decimals 
                data['ma_fastPeriod'] = data['Close'].rolling(window=7).mean()
                data['ma_slowPeriod'] = data['Close'].rolling(window=19).mean()
            except:
                print("No connexion ~ Data extraction")
                pass 
            # Check if ema fast > ema slow and if we the bot is in Long status 
            if data['ma_fastPeriod'][-2] > data['ma_slowPeriod'][-2] and longState:

                try:
                    stock_temp = get_stock_bot(symbol,'1m', "10 minute ago UTC", 'Close_time')
                    quantity = amount/stock_temp['Close'][-1]
                    #print(quantity)
                    quantity = quantity.round(2)
                    #print(quantity)
                    # Buy
                except:
                    print("No connexion ~ Data extraction before BUY")
                    pass
                try:
                    # Buy at the market price 
                    buy_order = client.order_market_buy(symbol=symbol, quantity=quantity)
                    # Check the order and extract variables
                    buy_origQty, buy_executedQty, buy_status, buy_price = check_order(buy_order)
                    buy_price = float(buy_price)
                    quantity = float(buy_executedQty)
                    priceStopLoss = buy_price - (buy_price * stopLoss)
                    priceTakeProfit = buy_price + (buy_price * takeProfit)
                    print("BUY: ", buy_price)
                    print("TP: ", priceTakeProfit)
                    print("quantity", quantity)
                    longState = False
                    shortState = True
                    buyStatus = True

                except:
                    print("No connexion ~ buy_order process")
                    pass
                
                try:
                    # Send a text via telegram
                    message = "BUY " + symbol + " at: "  + str(buy_price) + ' \n' + 'QUANTITY:' + str(buy_executedQty) + ' \n' + buy_status
                    telegram_send_message(message, chat_id, token=my_token)

                except:
                    print("No connexion ~ BUY send text")
                    pass

                # Ready to short with TP/SL or strategy condition

            # if the data at the time t in < or equal to the stop loss value and Short condition
            elif data['Close'][-2] <= priceStopLoss and shortState:

                try:
                    print('quantity',quantity)
                    print('type quantity',type(quantity))
                    # Sell at the narket price 
                    sell_order = client.order_market_sell(symbol=symbol, quantity=quantity)
                    # Check the order and extract variables
                    sell_origQty, sell_executedQty, sell_status, sell_price = check_order(sell_order)
                    sell_price = float(sell_price)
                    print("SELL: ", sell_price)
                    sell_executedQty = float(sell_executedQty)
                    # The new amount to invest in equal to the inital amount + the TP/SL price.
                    # Cumulative investment
                    amount = sell_executedQty * sell_price
                    # Ready to long
                    longState = True
                    shortState = False
                    buyStatus = False
                    quantity = float(sell_executedQty)
                except:
                    print("No connexion ~ SL SELL process")
                    pass

                try:
                    # Send a text via telegram
                    message_sell = "SL SELL " + symbol + " at: "  + str(sell_price) + ' \n' + 'QUANTITY:' + str(sell_executedQty) + ' \n' + sell_status
                    telegram_send_message(message_sell, chat_id, token=my_token)
                except:
                    print("No connexion ~ SL SELL send text")
                    pass
                
            # if the data at the time t in ? or equal to the take profit value and Short condition
            elif data['Close'][-1] > priceTakeProfit and shortState:

                try:
                    # Sell at the narket price 
                    sell_order = client.order_market_sell(symbol=symbol, quantity=quantity)
                    # Check the order and extract variables
                    sell_origQty, sell_executedQty, sell_status, sell_price = check_order(sell_order)
                    sell_price = float(sell_price)
                    sell_executedQty = float(sell_executedQty)
                    print("SELL: ", sell_price)
                    amount = sell_executedQty * sell_price
                    # Ready to long
                    longState = True
                    shortState = False
                    buyStatus = False

                except:
                    print("No connexion ~ TP SELL process")
                    pass

                try:
                    message_sell = "TP SELL " + symbol + " at: "  + str(sell_price) + ' \n' + 'QUANTITY:' + str(sell_executedQty) + ' \n' + sell_status
                    telegram_send_message(message_sell, chat_id, token=my_token)
                except:
                    print("No connexion ~ TP SELL send text")
                    pass

            # Check if ma fast < ma slow and if we the bot is in short status 
            # index -2 for the validation of the crossing. if it's index -1 it will buy at the next iteration
            # Because ma fast > ma slow at index -2 
            elif data['ma_fastPeriod'][-2] < data['ma_slowPeriod'][-2]:
                # if the coin has been buy then
                if buyStatus:
                    try:
                        # Sell at the narket price 
                        sell_order = client.order_market_sell(symbol=symbol, quantity=quantity)
                        # Check the order and extract variables
                        sell_origQty, sell_executedQty, sell_status, sell_price = check_order(sell_order)
                        sell_price = float(sell_price)
                        print("SELL: ", sell_price)
                        sell_executedQty = float(sell_executedQty)
                        amount = sell_executedQty * sell_price
                        # Ready to long
                        shortState = False
                        longState = True
                        buyStatus = False
                    except:
                        print("No connexion ~ SELL process")
                        pass
                    try:
                        message_sell = "SELL " + symbol + " at: "  + str(sell_price) + ' \n' + 'QUANTITY:' + str(sell_executedQty) + ' \n' + sell_status
                        telegram_send_message(message_sell, chat_id, token=my_token)
                    except:
                        print("No connexion ~ SELL send text")
                        pass
                # if the coin has not been buy before we can start a new cycle of buy sell.
                # The initial condition is first to wait to have a buy signal then sell.
                elif not buyStatus:
                    # Ready to long
                    longState = True
                    shortState = False

        time.sleep(10)