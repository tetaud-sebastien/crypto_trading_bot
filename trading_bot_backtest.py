import pandas as pd
import matplotlib.pyplot as plt 
import numpy as np
from datetime import datetime, timedelta
from binance.client import Client
from analytic_function import get_stock
import seaborn as sns
import analytic_function
import warnings
import os
import config
import glob
from strategy import profit_cumulative_calculation, advanced_analytics, strategy_v1_sl_tp_cap_cumul
warnings.filterwarnings('ignore')

# For a given strategy with SL TP AND EMA parameters, form back-test for all pairs 
# and save the annual performance for all pairs in a heatmap

# ------ FunctionS ------ #

def listdir_nohidden(path):
    return glob.glob(os.path.join(path, '*'))

if __name__ == "__main__":

    # ------ Parameters ------ #

    binance_api_source_key = config.BINANCE_API_SOURCE_KEY
    binance_api_sources_secret = config.BINANCE_API_SOURCE_SECRET
    client = Client(binance_api_source_key, binance_api_sources_secret)
    list_KLINE = config.KLINE
    path_data = config.PATH
    path_result = config.PATH_RESULT
    backtest_period = pd.Timedelta(days=config.BACKTEST_PERIOD_IN_DAYS)
    amount = config.AMOUNT
    fees = config.FEES
    stopLoss = config.STOPLOSS
    takeProfit = config.TAKEPROFIT
    grid_temp = pd.DataFrame(columns=list_KLINE)

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

                    buy_data, sell_data = strategy_v1_sl_tp_cap_cumul(data,fastperiod=12, slowperiod=26, stopLoss=stopLoss, takeProfit=takeProfit)


                    # Extract profit dataframe
                    profit = profit_cumulative_calculation(amount=amount, fees=fees , buy_price=buy_data, sell_price=sell_data, verbose = False)

                    # Perfome advanced analytics
                    # Number of Trade, Ratio Win/Loss
                    # Save or Show the result
                    analytical_df = advanced_analytics(data= data,buy_data=buy_data,sell_data=sell_data,symbol=symbol, kline=kline, profit= profit, show_plot=False, save_plot=True, path = path_result)
                    win_rate = float(analytical_df.loc['Ratio Win/Loss [%]'].values)
                    performance = float(analytical_df.loc['Performance [%]'].values)
                    profit_factor = float(analytical_df.loc['Profit factor'].values)

                    # append annual performance in % into a dataframe
                    grid_temp[kline][symbol] = performance

    # Generation of a performance dataFrame: coins vs candlesticks
    grid_performance = pd.DataFrame()
    for i in grid_temp.columns:

        df_grid_temp = grid_temp[i].to_frame()
        grid_performance = pd.concat([grid_performance,df_grid_temp],axis=1)
    
    fig, ax = plt.subplots(figsize=(20,100))
    ax = sns.heatmap(grid_performance,annot = True, cbar_kws={"orientation": "horizontal"},cmap='viridis_r')
    plt.savefig(path_result + "heatmap_annual_performace.png")