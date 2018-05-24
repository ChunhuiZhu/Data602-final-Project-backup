# -*- coding: utf-8 -*-
"""
Created on Wed May 23 10:51:19 2018

@author: czhu5
"""

import pandas as pd
import requests
import urllib.request as web
import json 
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings("ignore")
import time
import numpy as np
import datetime as DT
from pymongo import MongoClient
import matplotlib.pyplot as plt
from matplotlib.finance import candlestick2_ohlc
from dateutil.parser import parse
import itertools
import statsmodels.api as sm
plt.style.use('fivethirtyeight')
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.linear_model import LinearRegression
reg=LinearRegression()
from decimal import Decimal

#last100trade(symbol) will excutive after the trade confirmed
#return an array[ask, bid] to Trade() for order calculation 
def last100trade(symbol):
        #ticker="USDT-"+symbol
        url="https://bittrex.com/api/v1.1/public/getorderbook?market="+symbol+"&type=both"
        jdata=requests.get(url).json()
        if not bool(jdata):
            print("product is not exist!")
            return 
        else:
        #"sell" in API reflex to ask price
            ask=jdata["result"]["sell"]
            ask=pd.DataFrame(ask)
            ask.rename(columns={'Quantity':symbol+'.askV', 'Rate':symbol+'.askP'}, inplace=True)
            
            
            #"buy" in API reflex to bid price
            bid=jdata["result"]["buy"]
            bid=pd.DataFrame(bid)
            bid.rename(columns={'Quantity':symbol+'.bidV', 'Rate':symbol+'.bidP'}, inplace=True)
    
            lastprice=pd.concat([ask, bid], axis=1)
            	
            lastprice = lastprice.sort_index(ascending=False)
            return(lastprice)




#his100chart(company) will excutive after checking trader input is correct 
#get data by calling history100day(com)
#perform data visulatizations for last 100 days trading data
def last100tradechart(symbol1,symbol2,symbol3 ):
    #symbol=symbol.upper()
    lasttrade1=last100trade(symbol1)
    lasttrade2=last100trade(symbol2)
    lasttrade3=last100trade(symbol3)
    lasttrade=pd.concat([lasttrade1, lasttrade2], axis=1)
    lasttrade=pd.concat([lasttrade, lasttrade3], axis=1)

    lasttrade= lasttrade.reset_index(drop=True)
    lasttrade.round(5).astype(Decimal)
    lasttrade.reset_index(inplace=True)
    #print(lasttrade)
    
    #Assume I have amount of USD to buy 1 BTC (original investment), then I buy bitcoin
    lasttrade['method1Profit']=1/lasttrade['BTC-ETH.bidP']*lasttrade['USDT-ETH.bidP']-lasttrade['USDT-BTC.askP']
    lasttrade['method1Profit'].round(5).astype(Decimal)
    
    print(lasttrade['method1Profit'])
    #Assume I have amount of USD to buy 1 BTC (original investment), then I buy ETH
    lasttrade['method2Profit']=lasttrade['USDT-BTC.askP']/lasttrade['USDT-ETH.bidP']*lasttrade['BTC-ETH.askP']*lasttrade['USDT-BTC.bidP']-lasttrade['USDT-BTC.bidP']
    lasttrade['method2Profit'].round(5).astype(Decimal)
   
    print(lasttrade['method2Profit'])
    
    fig= plt.figure(figsize=(10,8))
    ax = fig.add_subplot(2, 1, 1)
    plt.title("Compare two aribitrage strategies in last 100 trades - bittrex.com")
    print("")
    plt.plot(lasttrade['method1Profit'],'k',lw=0.75,linestyle='-',label='1: short BTC, long ETH')
    plt.legend(loc=2,prop={'size':9.5})
    plt.ylabel('Profit')
    plt.grid(True)
    print("")
    
    bx = fig.add_subplot(2, 1, 2)
    plt.plot(lasttrade['method2Profit'],'k',lw=0.75,linestyle='-',label='2: short ETH, long BTC')
    plt.legend(loc=2,prop={'size':9.5})
    plt.ylabel('Profit')
    plt.grid(True)
    print("")

#"USDT-BTC", "BTC-ETH", "ETH-ADA"
last100tradechart("USDT-BTC", "USDT-ETH", "BTC-ETH")






















































