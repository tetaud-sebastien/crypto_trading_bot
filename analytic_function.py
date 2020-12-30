import pandas as pd
from influxdb import DataFrameClient
import numpy as np
from binance.client import Client
import telegram
import os 
from datetime import datetime
import config
# API Connection
# Telegram
# import config for Telegram
my_token = config.TELEGRAM_TOKEN
chat_id= config.TELEGRAM_CHAT_ID
# API Connection

binance_api_source_key = config.BINANCE_API_SOURCE_KEY
binance_api_sources_secret = config.BINANCE_API_SOURCE_SECRET

client = Client(binance_api_source_key, binance_api_sources_secret)
#client_db = DataFrameClient('localhost', 8086, 'root', 'root', 'BTC')
#client_db.create_database('BTC')


# ------ FunctionS ------ #

def export_to_influx_db(df, measurement, database):
    """

    :param df: dataframe 
    :param measurement: name of the measurement
    :param database: ame of the influx database
    :return:
    """

    client_db = DataFrameClient('localhost', 8086, 'root', 'root', database)

    # Transform Serie to Dataframe to use client.write_points Class
    # TypeError: Must be DataFrame, but type was: <class 'pandas.core.series.Series'>.

    #df = df.to_frame()
    field = df.columns[0]
    print('exported', field)
    # Extract first timestamp and last timestamp
    start = df.index[0]
    end = df.index[-1]

    try:
        client_db.write_points(df[start:end], measurement=measurement, database=database)
        print(field + ' from ' + str(start) + ' to ' + str(end) + ' exported to ' + measurement + ' db')
    except NameError:

        print('could not export ' + field + 'from ' + str(start) + ' to ' + str(end) + ' to ' + measurement + ' db')


def get_stock(symbol, interval, start, end, time_ref):
    klines = client.get_historical_klines(symbol=symbol, interval=interval, start_str=start, end_str=end)
    
    # Create dataframe with columns and data
    columns = ['Open_time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close_time', 'Quote_asset_volume',
               'Number_of_trades', 'Taker_buy_base_asset_volume', 'Taker_buy_quote_asset_volume',
               'Can_be_ignored']  
    df = pd.DataFrame(columns=columns, data=klines, dtype=float)
    df['Open_time'] = df['Open_time'].apply(lambda x: pd.to_datetime(datetime.utcfromtimestamp(int(x) / 1000)))
    df['Close_time'] = df['Close_time'].apply(lambda x: pd.to_datetime(datetime.utcfromtimestamp(int(x) / 1000)))
    df = df.set_index(time_ref)

    return df


def get_stock_bot(symbol, interval, period, time_ref):
    klines = client.get_historical_klines(symbol, interval, period)

    columns = ['Open_time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close_time', 'Quote_asset_volume',
               'Number_of_trades', 'Taker_buy_base_asset_volume', 'Taker_buy_quote_asset_volume',
               'Can_be_ignored']  # Create dataframe with columns and data
    df = pd.DataFrame(columns=columns, data=klines, dtype=float)
    df['Open_time'] = df['Open_time'].apply(lambda x: pd.to_datetime(datetime.utcfromtimestamp(int(x) / 1000)))
    df['Close_time'] = df['Close_time'].apply(lambda x: pd.to_datetime(datetime.utcfromtimestamp(int(x) / 1000)))
    df = df.set_index(time_ref)

    return df


def binance_order_book(SYMBOL='BTCUSDT'):
    '''''
    param: string
    return: string, string
    '''

    #  extract order book
    order_book = client.get_orderbook_ticker(symbol=SYMBOL)

    # extract ask price
    ask_price = order_book['askPrice']
    ask_qty = order_book['askQty']

    # extract sell price
    bid_price = order_book['bidPrice']
    bid_qty = order_book['bidQty']
    return float(ask_price), float(ask_qty), float(bid_price), float(bid_qty)


def check_order(order):
    
    df = pd.DataFrame(order)
    origQty = df['origQty'][0]
    executedQty = df['executedQty'][0]
    status = df['status'][0]
    price = df['fills'][0]['price']

    return origQty, executedQty, status, price


def telegram_send_message(msg, chat_id, token=my_token):
    """
    - After create a bot on telegram (BotFather)
    - Start Bot
    - https://api.telegram.org/bot**HTTP API**/getUpdates
    - take chat id
    - If it's in a group take the chat id with negative value
    
    Send a mensage to a telegram user specified on chatId
    chat_id must be a number!
    """
    bot = telegram.Bot(token=token)
    bot.sendMessage(chat_id=chat_id, text=msg)


def no_connexion_message():
    date_now = datetime.now()
    date_now = date_now.strftime("%m-%d-%Y, %H:%M:%S")

    return 'Connexion lost: ' + date_now

    
