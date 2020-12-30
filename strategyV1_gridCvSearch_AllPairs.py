#!interpreter
# -*- coding: utf-8 -*-
# Sebastien tetaud 2020-10-19
# Backatest with with EMA optmization for all coins with 1 year of data, all candles
# Find the Best performance 

import pandas as pd
import matplotlib.pyplot as plt 
import numpy as np
from datetime import datetime, timedelta
from binance.client import Client
from analytic_function import get_stock
import analytic_function
import warnings
import os
import glob
import config
from strategy import profit_cumulative_calculation, profit_calculation, advanced_analytics, profit_cumulative_calculation

warnings.filterwarnings('ignore')


# ------ FunctionS ------ #

def listdir_nohidden(path):
    return glob.glob(os.path.join(path, '*'))

# ------ FunctionS ------ #

# Parameters
binance_api_source_key = config.BINANCE_API_SOURCE_KEY
binance_api_sources_secret = config.BINANCE_API_SOURCE_SECRET
client = Client(binance_api_source_key, binance_api_sources_secret)
amount = config.AMOUNT
fees = config.FEES
kline = config.KLINE
start = config.START
end = config.END

if __name__ == "__main__":

    start_time = datetime.now() 
    # ------ Parameters ------ #
    api_key_binance = config.api_key_binance
    api_secret_binance = config.api_secret_binance
    client = Client(api_key_binance, api_secret_binance)
    list_KLINE = config.KLINE
    path_data = config.PATH
    path_result = config.PATH_RESULT
    backtest_period = pd.Timedelta(days=config.BACKTEST_PERIOD_IN_DAYS)
    amount = config.AMOUNT
    fees = config.FEES
    stopLoss = config.STOPLOSS
    takeProfit = config.TAKEPROFIT
    grid_temp = pd.DataFrame(columns=list_KLINE)

    stopLoss = np.arange(0.01, 0.06,0.01)
    takeProfit = np.arange(0.03, 0.1,0.01)
    fastperiod = np.arange(7, 14,1)
    slowperiod = np.arange(17, 30,1)
    best_perf = 0
    

    # loop to itererate backtest on all candlesticks
    for kline in list_KLINE:

        path_foldername = os.path.join(path_data,kline)
        print(path_foldername)

        # path of all folers which contains data
        # e.g: /Users/sebastientetaud/Documents/Python/trading/data/15m/
        files = listdir_nohidden(path_foldername)
        files = sorted(files)
        # loop to itererate backtest on all coins
        for file in files:

            # path of a file
            # e.g: /Users/sebastientetaud/Documents/Python/trading/data/15m/LINKUPUSDT.xlsx
            filename = os.path.join(path_foldername,file)
            print(filename)

            # Extract symbol from the file
            symbol = os.path.basename(file)
            symbol = symbol.replace(".xlsx","")
            print(symbol)

            # Open files
            df = pd.read_csv(filename) 
            df.index = df['Close_time']
            data = pd.DataFrame(df["Close"],index=pd.DatetimeIndex(df.index))

            if len(data):
                # Period check
                data_period = data.index[-1] - data.index[0]
                
                if data_period == backtest_period:
                    

                    
                    # Backtest for a given strategy
                    for maFast in fastperiod:

                        for maSlow in slowperiod:

                            for sl in stopLoss:
                            
                                for tp in takeProfit:

                                    # Execute strategy 
                                    buy_data, sell_data = strategy_v1_sl_tp(data=data, 
                                                                fastperiod=maFast, 
                                                                slowperiod=maSlow, 
                                                                stopLoss=sl,
                                                                takeProfit=tp)

                                    profit = profit_cumulative_calculation(amount=amount, fees=fees , 
                                                                buy_price=buy_data, sell_price=sell_data, 
                                                                verbose = False)

                                    analytical_df = advanced_analytics(data=data, buy_data=buy_data, sell_data=sell_data, symbol=symbol, kline=kline, profit= profit, show_plot=False, save_plot=False, path = path_result)
                                    win_rate = float(analytical_df.loc['Ratio Win/Loss [%]'].values)
                                    performance = float(analytical_df.loc['Performance [%]'].values)
                                    profit_factor = float(analytical_df.loc['Profit factor'].values)
                                    
                                    if performance > best_perf:

                                        best_perf = performance
                                        best_sl = sl
                                        best_tp = tp
                                        best_fastperiod = maFast
                                        best_slowperiod = maSlow
                                        best_kline = kline
                                        best_symbol = symbol
                                        best_profit_factor = profit_factor
                                        best_analytical_df = analytical_df

                    print("Profit Factor:", best_profit_factor)
                    print("Best Performance:",best_perf)
                    print("Stop Loss: ", best_sl)
                    print("Take Profit:", best_tp)
                    print("Fast MA: ", best_fastperiod)
                    print("Slow MA:", best_slowperiod)
                    print("Profit Factor:", best_profit_factor)
                    # re do the backtest with the best para and save the result 

                    # Execute strategy 
                    buy_data, sell_data = strategy_v1_sl_tp(data=data, fastperiod=best_fastperiod, slowperiod=best_slowperiod, stopLoss=best_sl, takeProfit=best_tp)
                    profit = profit_cumulative_calculation(amount=amount, fees=fees ,buy_price=buy_data, sell_price=sell_data, verbose = False)
                    analytical_df = advanced_analytics(data=data, buy_data=buy_data, sell_data=sell_data, symbol=symbol, kline=kline, profit= profit, show_plot=False, save_plot=True, path = path_result)

                    df_best_param = pd.DataFrame(data=[best_slowperiod, best_fastperiod ,best_sl,best_tp], 
                                         columns=['Values'],
                                         index=['best_slowperiod','best_fastperiod','stop loss','take profit'])

                    analytical_df = pd.concat([best_analytical_df,df_best_param],axis=0)
                    print(analytical_df)
                    # Save advanced analytics into a txt file

                    analytics_filename = "advanced_analytics.txt"
                    path_result_kline  = os.path.join(path_result,kline)
                    path_result_kline = os.path.join(path_result_kline,analytics_filename)
                    print(path_result_kline)
                    f=open(path_result_kline, "a+")
                    f.write("\n" )
                    f.write("----" + symbol +"---- \n" )
                    f.write("\n" )
                    f.close()
                    analytical_df.to_csv(path_result_kline, header=False, index=True, sep='\t', mode='a')

                    # Reset performance
                    best_perf = 0
                    

    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))