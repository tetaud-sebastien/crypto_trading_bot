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
warnings.filterwarnings('ignore')

def profit_calculation(amount, fees , buy_price, sell_price , verbose = False):
    
    buy_price_values = buy_price.values
    sell_price_values = sell_price.values

    quantity = amount/buy_price_values
    quantity = quantity - (fees*quantity)
    index = sell_price.index
    total_growth = quantity * sell_price_values
    total_sell = total_growth - (total_growth*fees)
    profit = (total_sell - amount)

    if verbose:
        print("Total Buy:", amount)
        print("Quantity after fees:" , quantity)
        print("Total sell growth:",total_growth)
        print("Total after fees:",total_sell)
        print("Transaction fees:", total_growth -total_sell)
        print("Take Profit:", profit)
    
    profit = pd.DataFrame({'profit':profit}, index=pd.DatetimeIndex(index))

    return profit


def profit_cumulative_calculation(amount, fees, buy_price, sell_price, verbose = False):
    
    
    list_profit =[]
    amount_init = amount
    for i in range(len(buy_price)):
        
        
        quantity = amount/buy_price[i]
        quantity = quantity - (fees*quantity)
        index = sell_price.index[i]
        total_growth = quantity * sell_price[i]
        total_sell = total_growth - (total_growth*fees)
        profit = (total_sell - amount)
        
        amount = amount + profit
       #print(index, "|", buy_data[i], "|", sell_price[i], "|", amount)
        list_profit.append(profit)
        
        
        

    if verbose:
        print("Total Buy:", amount)
        print("Quantity after fees:" , quantity)
        print("Total sell growth:",total_growth)
        print("Total after fees:",total_sell)
        print("Transaction fees:", total_growth -total_sell)
        print("Take Profit:", amount_init - list_profit[-1])
    
    profit = pd.DataFrame({'profit':list_profit}, index=pd.DatetimeIndex(sell_price.index))

    return profit


def advanced_analytics(data,buy_data,sell_data, symbol, kline, profit, show_plot, save_plot, path):

    monthly_profit = profit.groupby([profit.index.month_name()], sort=False).sum().eval('profit')
    
    # Advanced statistics 
    
    nb_trade = len(profit)
    performance = profit.sum()[0]
    performance = round(performance,2)
    profit_factor = profit[profit['profit'] > 0].sum()/-(profit[profit['profit'] < 0].sum())
    profit_factor = profit_factor[0]
    profit_factor = round(profit_factor,2)
    max_drawdown = profit.min()[0]
    max_drawdown = round(max_drawdown,2)
    win_rate = np.sum((profit > 0).values.ravel())*100 /len(profit)
    win_rate = round(win_rate,2)
    #print('Number of Trade ',nb_trade)
    #print('Number of + Trade ',np.sum((profit > 0).values.ravel()))
    #print('win rate: ',np.sum((profit > 0).values.ravel())*100 /len(profit) )
    #print("Performance = {0:.2f}".format(performance))
    #print("Profit factor = {0:.2f}".format(profit_factor))
    #print("Max Drawdown = {0:.2f}".format(max_drawdown))
    

    # PLOT
    fig, axs = plt.subplots(3,figsize=(15,20),constrained_layout=True)
    axs[0].plot(data['Close'],label = 'Close',alpha=0.8)
    axs[0].scatter(buy_data.index,buy_data,label='Buy',marker='^',color='green')
    axs[0].scatter(sell_data.index,sell_data,label='Sell',marker='v',color='red')
    axs[0].set_title( symbol + ' Close Price History Buy and Sell Signals',fontsize=18)
    axs[0].set_ylabel('UDST',fontsize=16)
    axs[0].legend(loc='upper right')
    axs[0].grid()
    #ax2.figure(figsize=(16,8))
    axs[1].set_title('Profit',fontsize=18)
    axs[1].plot(profit.cumsum(),'-o',label="Total profit={0:.3f}".format(profit.sum()[0]))
    axs[1].set_ylabel('UDST',fontsize=16)
    axs[1].grid()
    axs[1].legend()
    monthly_profit.plot(kind='bar')
    axs[2].set_title("Mothly Performance",fontsize=18)
    axs[2].set_ylabel("Mothly profit in % ",fontsize=16)
    axs[2].set_xlabel("Month",fontsize=16)
    axs[2].grid()
    table_data=[
    ["Number of Trade", nb_trade],
    ["Ratio Win/Loss [%]",win_rate],
    ["Performance [%]", performance],
    ["Profit factor", profit_factor],
    ["Max Drawdown [%]", max_drawdown]]
    table =  axs[2].table(cellText=table_data,loc='bottom', bbox=[0, -1, 0.6, 0.6])
    table.auto_set_font_size(False)
    table.set_fontsize(22)
    table.scale(1,4)
    
    if show_plot:
        plt.show()

    if save_plot:

        path = os.path.join(path,kline)
        if not os.path.isdir(path):
        
            os.mkdir(path)

            print("Create %s repository" % path)

        filename = os.path.join(path,symbol)
        print(filename + ".png")
        plt.savefig(filename + ".png",bbox_inches="tight")
    
    plt.close()
    analytical_df = pd.DataFrame(data=table_data,columns=['Statistics','Values'])
    analytical_df = analytical_df.set_index('Statistics')
    return analytical_df


def strategy_v1_sl_tp_cap_cumul(data,fastperiod, slowperiod, stopLoss, takeProfit):
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

    ## EMA 
    data['fastperiod'] = data['Close'].rolling(window=fastperiod).mean()
    data['slowperiod'] = data['Close'].rolling(window=slowperiod).mean()
    
    
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
        
        
        if data['fastperiod'][i] > data['slowperiod'][i] and long_state == True:
            
            
            sigPriceBuy.append(data['Close'][i])
            sigPriceSell.append(np.nan)
            long_state = False
            short_state = True
            buy_status = True
            
            buy_price = data['Close'][i]
            price_sl = buy_price - (buy_price * stopLoss)
            price_tp = buy_price + (buy_price * takeProfit)
            #print("BUY: ", buy_price)


        
        elif data['Close'][i] <= price_sl and short_state == True:
             
            #print('SL SELL:',data['Close'][i])
            sigPriceBuy.append(np.nan)
            sigPriceSell.append(data['Close'][i])
            long_state = True
            short_state = False
            buy_status = False
            #print("---")
            
          
        elif data['Close'][i] >= price_tp and short_state == True:
               
            #print('TP SELL:',data['Close'][i])
            sigPriceBuy.append(np.nan)
            sigPriceSell.append(data['Close'][i])
            buy_status = False
            short_state = False
            #print("---")
            
            
        elif data['fastperiod'][i] < data['slowperiod'][i] :
           
        
            if short_state == True:
                #print('SELL:',data['Close'][i])
                sigPriceBuy.append(np.nan)
                sigPriceSell.append(data['Close'][i])
                short_state = False
                long_state = True
                buy_status = False
                #print("---")
                
            elif buy_status == False:
                
                long_state = True
                short_state = False
                sigPriceBuy.append(np.nan)
                sigPriceSell.append(np.nan)
                
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
