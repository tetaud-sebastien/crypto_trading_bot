import pandas as pd
import matplotlib.pyplot as plt 
import numpy as np
from datetime import datetime, timedelta
from binance.client import Client
from analytic_function import get_stock
import pandas_bokeh
import analytic_function
import warnings
import os
import glob
import config
from strategy import profit_cumulative_calculation, advanced_analytics, strategy_v1_sl_tp

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
path_result = config.PATH_RESULT
kline = '6h'
start = config.START
end = config.END
symbol = "BATUSDT"

if __name__ == "__main__":

    start_time = datetime.now()

    api_key_binance = config.api_key_binance
    api_secret_binance = config.api_secret_binance
    client = Client(api_key_binance, api_secret_binance)

    amount = config.AMOUNT
    fees = config.FEES
    stopLoss = np.arange(0.01, 0.10,0.01)
    takeProfit = np.arange(0.03, 0.1,0.01)
    fastperiod = np.arange(7, 14,1)
    slowperiod = np.arange(17, 30,1)

    best_fastperiod = 0
    best_slowperiod = 0
    best_perf = 0
    best_sl = 0
    best_tp = 0
    best_win_rate = 0
    best_kline = 0
    best_symbol = 0
    
    #Exatract data 
    df = get_stock(symbol = symbol, interval=kline, start=start,end=end, time_ref='Close_time')
    print(df)
    data = pd.DataFrame(df['Close'],index=df.index)
    stopLoss = np.arange(0.01, 0.10,0.01)
    takeProfit = np.arange(0.03, 0.1,0.01)
    fastperiod = np.arange(7, 14,1)
    slowperiod = np.arange(17, 30,1)
    best_fastperiod = 0
    best_slowperiod = 0
    best_perf = 0
    best_sl = 0
    best_tp = 0
    best_win_rate = 0
    best_profitFactor = 0 
    
    for emaf in fastperiod:
        
        for emas in slowperiod:
     
            for sl in stopLoss:
            
                for tp in takeProfit:
            
                    # Execute strategy 
                    buy_data, sell_data = strategy_v1_sl_tp(data=data, 
                                                            fastperiod=emaf, 
                                                            slowperiod=emas, 
                                                            stopLoss=sl,
                                                            takeProfit=tp)
        
                    profit = profit_cumulative_calculation(amount=amount, fees=fees , 
                                                buy_price=buy_data, sell_price=sell_data, 
                                                verbose = False)
                
                    analytical_df = advanced_analytics(data= data,buy_data=buy_data,sell_data=sell_data,
                                                        symbol=symbol, kline=kline, 
                                                        profit= profit, show_plot=False, 
                                                        save_plot=False, path = path_result)

                    nb_trade = float(analytical_df.loc['Number of Trade'].values)
                    win_rate = float(analytical_df.loc['Ratio Win/Loss [%]'].values)
                    performance = float(analytical_df.loc['Performance [%]'].values)
                    profit_factor = float(analytical_df.loc['Profit factor'].values)
                    max_drawdown = float(analytical_df.loc['Max Drawdown [%]'].values)

                    if performance > best_perf:
                        
                        best_strategy_nb_trade = nb_trade
                        best_strategy_win_rate = win_rate
                        best_perf = performance
                        best_profit_factor = profit_factor
                        best_strategy_max_drawdown = max_drawdown
                        best_sl = sl
                        best_tp = tp
                        best_fastperiod = emaf
                        best_slowperiod = emas
               
    
    print("Best Performance:",best_perf )
    print("Stop Loss: ", best_sl)
    print("Take Profit:", best_tp)
    print("Fast EMA: ", best_fastperiod)
    print("Slow EMA:", best_slowperiod)
    print("Profit Factor:", best_profit_factor)
    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))
    df = get_stock(symbol = symbol, interval=kline, start=start,end=end, time_ref='Close_time')
    print(df)
    data = pd.DataFrame(df['Close'],index=df.index)
    buy_data, sell_data = strategy_v1_sl_tp(data=data,fastperiod=best_fastperiod, slowperiod=best_slowperiod, stopLoss=best_sl,takeProfit=best_tp)
    profit = profit_cumulative_calculation(amount=amount, fees=fees, buy_price=buy_data, sell_price=sell_data, verbose = False)        
    analytical_df = advanced_analytics(data=data, buy_data=buy_data, sell_data=sell_data, symbol=symbol, kline=kline, profit= profit, show_plot=False, save_plot=True, path =path_result)

