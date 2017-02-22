import os.path
import pandas as pd
import requests
from datetime import datetime
from datetime import timedelta
import matplotlib
import matplotlib.pyplot as plt
import pyfolio as pf
import pandas_datareader.data as web

now = datetime.now()
start = datetime.strptime("01-02-2014", "%m-%d-%Y")
##base_url = 'http://ws.spk.gov.tr/PortfolioValues/api/PortfoyDegerleri/'

portfolio = pd.DataFrame({'Name': [],'Number': [],'Price': []})
backtrack = pd.DataFrame(index=pd.date_range(start, now, dtype='datetime64[ns]'), columns = ['MarketValue', 'Cost', 'ReturnSeries'])
backtrack = backtrack.fillna(0)
money = int(raw_input("Starting money:"))
monthly_money = int(raw_input("Montly investment:"))
#Stock code list and their percentages.
code_list = []
code_list_perc = []
number_of_inputs = int(raw_input("Number of stocks:"))

for i in range(0,number_of_inputs):
    #Stock name and percentages
    stock_name = str(raw_input("Name of the stock:"))
    stock_percentage = float(raw_input("Stock percentage:"))
    code_list.append(stock_name)
    code_list_perc.append(stock_percentage)
    #Getting the initial stock variables.
    ##resp = requests.get(base_url + stock_name + "/2/" + "01-02-2014/01-02-2014")
    resp = web.DataReader(stock_name, 'yahoo', start, end)['Adj Close']
    for item in resp:
        number_of_stocks = (stock_percentage * money) / item
        s = pd.Series([stock_name, number_of_stocks, item], index = ['Name', 'Number', 'Price'])
    portfolio = portfolio.append(s, ignore_index=True)

portfolio['Value'] = portfolio.Number * portfolio.Price
#Determining the initial backtrack positions.
backtrack.ix[start, 'MarketValue'] = portfolio['Value'].sum()
backtrack.ix[start, 'Cost'] = portfolio['Value'].sum()
start = start + timedelta(days=1)
i = 0
for stock in code_list:
    #Getting the .json data for certain stock.
    start_date = datetime.strftime(start, '%m-%d-%Y')
    end_date = datetime.strftime(now, '%m-%d-%Y')
    second_base_url = base_url + stock + "/2/" + start_date + "/" + end_date
    ##response = requests.get(second_base_url, timeout=None)
    response = web.DataReader(stock_name, 'yahoo', start, end)['Adj Close']
    #Calculating the money for certain stock.
    money_for_stock = money * code_list_perc[i]
    stock_month = 1
    for item in response.json():
        date_string= str(item['Tarih']).split('T')[0]
        my_date = datetime.strptime(date_string, '%Y-%m-%d')
        portfolio.ix[i,'Price'] = item['BirimPayDegeri']
        backtrack.ix[my_date, 'MarketValue'] += portfolio.ix[i,'Number'] * portfolio.ix[i,'Price']
        backtrack.ix[my_date, 'Cost'] += money_for_stock
        back_date = my_date - timedelta(days=1)
        while (backtrack.ix[back_date, 'MarketValue'] == 0):
            back_date = back_date - timedelta(days=1)
        backtrack.ix[my_date, 'ReturnSeries'] = (backtrack.ix[my_date, 'MarketValue'] /
        (backtrack.ix[back_date, 'MarketValue'] +
        (backtrack.ix[my_date, 'Cost'] - backtrack.ix[back_date, 'Cost']))) - 1
        #Doing the montly investment.
        if (my_date.month != stock_month):
            money_for_stock += monthly_money * code_list_perc[i]
            stock_month += 1
            if stock_month == 13 : stock_month = 1
            portfolio.ix[i,'Number'] += (monthly_money * code_list_perc[i]) / item['BirimPayDegeri']
    #Increasing i for the next stocks percentage.
    i += 1
backtrack = backtrack[backtrack.MarketValue != 0]
plt.plot(backtrack['ReturnSeries'])
plt.savefig('x.png')
new = backtrack['ReturnSeries']
new = new.tz_localize('utc')
print (new)
print (pf.create_returns_tear_sheet(new))
