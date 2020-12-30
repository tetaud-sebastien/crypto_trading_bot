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
from strategy import profit_cumulative_calculation, advanced_analytics

warnings.filterwarnings('ignore')


# ------ FunctionS ------ #

def listdir_nohidden(path):
    return glob.glob(os.path.join(path, '*'))


def indentify_outliers(row, n_sigmas=3): 
    x = row['simple_rtn']
    mu = row['mean']
    sigma = row['std']
    #if (x > mu + 3 * sigma) | (x < mu - 3 * sigma): 
    #if (x > mu + 3 * sigma): 
    if (x < mu - 3 * sigma):
        return 1
    else:
        return 0

def strategy_outliers_sl_tp_cap_cumul(data,df_outliers, stopLoss, takeProfit):
    """ 
    BUY when fastperiod > slowperiod
    SELL when reach TP or SL or fastperiod < slowperiod
    Cumulative trading
    :param data: dataframe for a given coins
    :param type: dataframe
    :param tp: take profit in %
    :param type: float

    return buy_data, sell_data
    """

    
    sigPriceBuy=[]
    sigPriceSell=[]
    long_state = True
    short_state = False
    buy_status = False
    buy_price = 0
    price_sl = 0
    price_tp = 0
 
    print('Backtest..')
    print('----------')
    for i in range(len(data)):
        
        
        if df_outliers['outlier'][i] == 1 and long_state == True:
            
            
            sigPriceBuy.append(data['Close'][i])
            sigPriceSell.append(np.nan)
            long_state = False
            short_state = True
            buy_status = True
            
            buy_price = data['Close'][i]
            price_sl = buy_price - (buy_price * stopLoss)
            price_tp = buy_price + (buy_price * takeProfit)
            print("BUY: ", buy_price)
            print("SL:",price_sl )
            print("TP:",price_tp )


        
        elif data['Close'][i] <= price_sl and short_state == True:
             
            print('SL SELL:',data['Close'][i])
            sigPriceBuy.append(np.nan)
            sigPriceSell.append(data['Close'][i])
            long_state = True
            short_state = False
            buy_status = False
            print("---")
            
          
        elif data['Close'][i] >= price_tp and short_state == True:
               
            print('TP SELL:',data['Close'][i])
            sigPriceBuy.append(np.nan)
            sigPriceSell.append(data['Close'][i])
            buy_status = False
            short_state = False
            long_state = True
            print("---")
            
                
        else:
            sigPriceBuy.append(np.nan)
            sigPriceSell.append(np.nan)

    data['Buy_Signal_Price']=sigPriceBuy
    data['Sell_Signal_Price']=sigPriceSell
    # drop nan just to have serie of buy and sell price
    sell_data = data['Sell_Signal_Price'].dropna()
    buy_data = data['Buy_Signal_Price'].dropna()
    
    # Check if sell_data and sell_data are not empty 
    if len(sell_data) and len(buy_data):
        if sell_data.index[0] < buy_data.index[0] and buy_data.index[-1] > sell_data.index[-1]:
            sell_data = sell_data[1:]
            buy_data = buy_data[:-1]
           
        elif sell_data.index[0] < buy_data.index[0]: 
            buy_data=buy_data[1:]
            sell_data = sell_data[:-1]
        
        elif buy_data.index[-1] > sell_data.index[-1]:
            buy_data = buy_data[:-1]

    return buy_data, sell_data

# ------ FunctionS ------ #

api_key_binance = config.api_key_binance
api_secret_binance = config.api_secret_binance
client = Client(api_key_binance, api_secret_binance)
amount = config.AMOUNT
fees = config.FEES
path_result = config.PATH_RESULT
kline = '1h'
start = config.START
end = config.END
symbol = "BTCUSDT"

if __name__ == "__main__":

    start_time = datetime.now()

    api_key_binance = config.api_key_binance
    api_secret_binance = config.api_secret_binance
    client = Client(api_key_binance, api_secret_binance)

    amount = config.AMOUNT
    fees = config.FEES
    stopLoss = np.arange(0.01, 0.10,0.01)
    takeProfit = np.arange(0.03, 0.1,0.01)
    


    best_perf = 0
    best_sl = 0
    best_tp = 0
    best_win_rate = 0
    best_kline = 0
    best_window = 0 
    best_profitFactor = 0 
    
    
    #Exatract data 
    df = get_stock(symbol = symbol, interval=kline, start=start,end=end, time_ref='Close_time')
    print(df)
    #data = pd.DataFrame(df['Close'],index=df.index)
    df['simple_rtn'] = df['Close'].pct_change()
    
    stopLoss = np.arange(0.01, 0.10,0.01)
    takeProfit = np.arange(0.03, 0.1,0.01)
    fastperiod = np.arange(7, 14,1)
    slowperiod = np.arange(17, 30,1)
    window = np.arange(5, 50,1)
    
    for w in window:

        df_rolling = df[['simple_rtn']].rolling(window=w).agg(['mean', 'std'])
        df_rolling.columns = df_rolling.columns.droplevel()
        df_outliers = df.join(df_rolling)

        df_outliers['outlier'] = df_outliers.apply(indentify_outliers, axis=1)
        outliers = df_outliers.loc[df_outliers['outlier'] == 1, ['simple_rtn']]
        outliers_index = outliers.index

        for sl in stopLoss:
        
            for tp in takeProfit:
        
                # Execute strategy 
                buy_data, sell_data = strategy_outliers_sl_tp_cap_cumul(data=df, df_outliers=df_outliers,
                                                        stopLoss=sl,
                                                        takeProfit=tp)
                if len(buy_data)==0 and len(sell_data)==0:
                    continue
                profit = profit_cumulative_calculation(amount=amount, fees=fees , 
                                            buy_price=buy_data, sell_price=sell_data, 
                                            verbose = False)
            
                analytical_df = advanced_analytics(data= df,buy_data=buy_data,sell_data=sell_data,
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
                    best_window = w

           
    
    print("Best Performance:",best_perf )
    print("Stop Loss: ", best_sl)
    print("Take Profit:", best_tp)
    print("Window: ", best_window)
    print("Profit Factor:", best_profit_factor)
    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))
    df = get_stock(symbol = symbol, interval=kline, start=start,end=end, time_ref='Close_time')
    print(df)
    

    buy_data, sell_data = strategy_outliers_sl_tp_cap_cumul(data=df, df_outliers=df_outliers,
                                                        stopLoss=sl,
                                                        takeProfit=tp)
    profit = profit_cumulative_calculation(amount=amount, fees=fees, buy_price=buy_data, sell_price=sell_data, verbose = False)        
    analytical_df = advanced_analytics(data=data, buy_data=buy_data, sell_data=sell_data, symbol=symbol, kline=kline, profit= profit, show_plot=False, save_plot=True, path =path_result)

