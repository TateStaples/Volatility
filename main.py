import numpy as np
import yfinance as yf
import pandas as pd
import datetime
from technical_rating import net_indicator



if __name__ == '__main__':
    tickers = pd.read_csv("tickers.csv")["Symbol"].tolist()
    volatility_df = pd.DataFrame()
    for symbol in tickers:
        data = yf.download(tickers=[symbol], period="600d", interval="1d")
        for day in range(365):
            # get data for 'day' days ago
            day_data = data.iloc[:-day-1]
            price = day_data.tail(1)["Close"][0]
            today = day_data.tail(1)  # data from today

            # Prices
            price = day_data.tail(1)["Close"][0]
            change = (day_data.tail(1)["Close"][0] - day_data.tail(2)["Close"][0])
            percent_change = change / day_data.tail(2)["Close"][0]

            # Volatility
            volatility_1D = (today["High"] - today["Low"]) / today["Close"]
            # next-day price

            # Technical Rating: https://www.tradingview.com/support/solutions/43000614331-technical-ratings/
            rating = net_indicator(day_data)
            # Sector
            tickerdata = yf.Ticker(symbol)
    # print(tickerdata.info)

