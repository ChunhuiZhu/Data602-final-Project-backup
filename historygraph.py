# -*- coding: utf-8 -*-
"""
Created on Thu May 17 12:27:40 2018

@author: czhu5
"""
import pandas as pd
import requests
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings("ignore")
import datetime as DT
import matplotlib.pyplot as plt
from matplotlib.finance import candlestick2_ohlc
from dateutil.parser import parse
plt.style.use('fivethirtyeight')
from sklearn.linear_model import LinearRegression
reg=LinearRegression()



#https://www.quantinsti.com/blog/build-technical-indicators-in-python/


def historyprice(com,numdays):   
    #use datatime function to calculate the date before 100 days
    #and store as backdate base on the designed formate
    today=DT.date.today()
    backdate= today-DT.timedelta(days=numdays)
    formate='%Y%m%d'
    backdate=backdate.strftime(formate)
    today=today.strftime(formate)

    #assign today and back100date to url date range
    #https://coinmarketcap.com/currencies/bitcoin/historical-data/?start=20180305&end=20180404
    url="https://coinmarketcap.com/currencies/"+com+"/historical-data/?start="+backdate+"&end="+today
    soup = BeautifulSoup(requests.get(url, "lxml").content)
    headings=[th.get_text() for th in soup.find("tr").find_all("th")]
    
    histdata=[]
    for row in soup.find_all("tr")[1:]:
        rowdata = list(td.get_text().replace(",","") for td in row.find_all("td"))
        histdata.append(rowdata)   

    #stor histroy data in a panda df his100
    #Change the type of datetime and order data by date
    hist=pd.DataFrame(histdata,columns=headings)
    hist=hist.convert_objects(convert_numeric=True)
    
    hist['Date'] = [parse(d).strftime('%Y-%m-%d') for d in hist['Date']]
    hist=hist.sort_values(by='Date')
    #hist.index = hist.Date
    return(hist)




#Analysis: CCI can be used to determine overbought and oversold levels. Readings above +100 
#can imply an overbought condition, while readings below −100 can imply an oversold condition.
# Commodity Channel Index 
def CCI(histdata, ndays): 
     TP = (histdata['High'] +histdata['Low'] + histdata['Close']) / 3 
     #The index is scaled by an inverse factor of 0.015 to provide for more readable numbers.
     C = pd.Series((TP - pd.rolling_mean(TP, ndays)) / (0.015 * pd.rolling_std(TP, ndays)), name = 'CCI') 
     histdata = histdata.join(C) 
     return histdata


#Moving Averages
# Simple Moving Average 
def SMA(histdata, ndays): 
     SMA = pd.Series(pd.rolling_mean(histdata['Close'], ndays), name = 'SMA_'+ str(ndays)) 
     histdata = histdata.join(SMA) 
     return histdata


# Exponentially-weighted Moving Average 
def EWMA(histdata, ndays): 
     EMA = pd.Series(pd.ewma(histdata['Close'], span = ndays, min_periods = ndays - 1), 
     name = 'EWMA_' + str(ndays)) 
     histdata = histdata.join(EMA) 
     return histdata
 
    
#The Rate of Change (ROC) is a technical indicator that measures the percentage change between 
#the most recent price and the price “n” day’s ago. The indicator fluctuates around the zero line.
#ROC = [(histdata['Close']- histdata['Close'].shift(-7)) / histdata['Close'].shift(-7)]
#exmpale use 7 days period Rate of change for NIFTY
def ROC(histdata,n):
     N = histdata['Close'].diff(n)
     D = histdata['Close'].shift(n)
     ROC = pd.Series(N/D,name='Rate of Change')
     histdata = histdata.join(ROC)
     return histdata




    
#his100chart(company) will excutive after checking trader input is correct 
#get data by calling history100day(com)
#perform data visulatizations for last 100 days trading data
def his100chart(company,numdays):
    company=company.lower()
    histdata=historyprice(company,numdays)
    histdata.reset_index(inplace=True)

    #show 20 day moving averages
    #print("Last 100-day trade history chart")
    vdiff=histdata['Volume'].diff(1)
    
    # Compute the 7-day SMA
    SMAdf= SMA(histdata,7)
    SMAdf= SMAdf.dropna()
    SMAdata = SMAdf['SMA_7']
    
    
    # Compute the 20-day EWMA 
    EWMAdf= EWMA(histdata,20)
    EWMAdf= EWMAdf.dropna()
    EWMAdata = EWMAdf['EWMA_20']

    CCIdf = CCI(histdata, 7)
    CCIdata = CCIdf['CCI']
    
    ROCdf = ROC(histdata,7)
    ROCdata= ROCdf['Rate of Change']
    
    
    
    fig= plt.figure(figsize=(10,8))
    ax = fig.add_subplot(4, 1, 1)
    plt.ylabel("USD Price")
    plt.title(company+"/USD "+"in Last "+ str(numdays)+" days - CoinMarketCap.com")
    candlestick2_ohlc(ax, histdata["Open"], histdata["High"], histdata["Low"], histdata["Close"], width=1, colorup='g')
    
    plt.plot(SMAdata,'b',lw=1, label='7-day SMA (blue)')
    plt.plot(EWMAdata,'m', lw=1, label='20-day EWMA (purple)')
    plt.legend(loc=2,prop={'size':11})
    plt.grid(True)
    print("")
    print("")
    
    bx = fig.add_subplot(4, 1, 2)
    plt.plot(vdiff,'k',lw=0.75,linestyle='-',label='$B daily difference')
    plt.legend(loc=2,prop={'size':9.5})
    plt.ylabel('Volumn change')
    plt.grid(True)
    print("")
    
    cx = fig.add_subplot(4, 1, 3)
    plt.plot(CCIdata,'k',lw=0.75,linestyle='-',label='weekly CCI')
    plt.legend(loc=2,prop={'size':9.5})
    plt.ylabel('CCI values')
    plt.grid(True)
    print("")
    
    dx = fig.add_subplot(4, 1, 4)
    plt.plot(ROCdata,'k',lw=0.75,linestyle='-',label='Weekly ROC')
    plt.legend(loc=2,prop={'size':9.5})
    plt.ylabel('ROC values')
    plt.grid(True)    
        
    plt.show()



decision=str(input("Please enter company (bitcoin):  ")) 
 
his100chart("bitcoin",100) 



    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    