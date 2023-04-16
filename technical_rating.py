import math

import pandas as pd
import yfinance as yf
from ta.momentum import *
from ta.trend import *
from ta.volume import *


def rising(df: pd.Series) -> bool: return last(df) > last(df, 2)


def last(df: pd.Series, n: int = 1) -> float: return df.tail(n)[0]


def net_indicator(df: pd.Series):
    df = yf.download(symbol, start=start_date)  # , end=end_date)
    high = df["High"]
    low = df["Low"]
    close = df["Close"]
    volume = df["Volume"]
    price = close.tail(1)[0]
    # Calculate the technical indicators
    indicators = []
    # Moving Averages (SMA and EMAs for each lags): Buy — MA value < price, Sell — MA value > price
    ma_lengths = [10, 20, 30, 50, 100, 200]
    sma = [last(sma_indicator(close, length)) for length in ma_lengths]
    ema = [last(ema_indicator(close, length)) for length in ma_lengths]
    for value in sma: indicators.append(1 if value < price else -1)
    for value in ema: indicators.append(1 if value < price else -1)
    # the Ichimoku Cloud (9, 26, 52): Buy — base line < price and conversion line crosses price from below and lead line 1 > price and lead line 1 > lead line 2, Sell — base line > price and conversion line crosses price from above and lead line 1 < price and lead line 1 < lead line 2
    ichi = IchimokuIndicator(high=high, low=low)
    baseline = 0
    conversion = 0
    a = 0
    b = 0
    indicators.append(
        1 if baseline < price and a > price and a > b else -1 if baseline > price and b < price and b > a else 0)
    # VWMA (20)
    vwap = volume_weighted_average_price(high, low, close, volume, window=20)
    indicators.append(1 if last(vwap) < price else -1)
    # HullMA (9).
    n = 9
    wma = lambda n: wma_indicator(close, n)
    hma = wma_indicator(2 * wma(int(n // 2)) - wma(n), int(math.sqrt(n)))
    indicators.append(1 if last(hma) < price else -1)

    # RSI (14): Buy — indicator < 30 and rising, Sell — indicator > 70 and falling
    rsi = rsi(close=close)
    indicators.append(1 if last(rsi) < 30 and rising(rsi) else -1 if last(rsi) > 70 and not rising(rsi) else 0)
    # Stochastic (14, 3, 3),Buy — main line < 20 and main line crosses over the signal line, Sell — main line > 80 and main line crosses under the signal line
    stoch = last(stoch(high=high, low=low, close=close))
    stoch_signal = last(stoch_signal(high=high, low=low, close=close))
    indicators.append(1 if stoch < 20 and stoch < stoch_signal else -1 if stoch > 80 and stoch > stoch_signal else 0)
    # CCI (20): Buy — indicator < -100 and rising Sell — indicator > 100 and falling
    cci = cci(high=high, low=low, close=close)
    indicators.append(1 if last(cci) < -100 and rising(cci) else -1 if last(cci) > 100 and not rising(cci) else 0)
    # ADX (14, 14): Buy — indicator > 20 and +DI line crosses over -DI line, Sell — indicator > 20 and +DI line crosses under -DI line
    indicator = ADXIndicator(high=high, low=low, close=close)
    adx, neg, pos = last(indicator.adx()), last(indicator.adx_neg()), last(indicator.adx_pos())
    indicators.append(1 if adx > 20 and pos > neg else -1 if adx > 20 and neg > pos else 0)
    # AO: Buy — saucer and values are greater than 0, or cross over the zero line, Sell — saucer and values are lower than 0, or cross under the zero line
    ao = AwesomeOscillatorIndicator(high=high, low=low).awesome_oscillator()
    # todo: add indicator
    # Momentum (10): Buy — indicator values are rising Sell — indicator values are falling
    momentum = last(roc(close=close, window=10))
    indicators.append(1 if momentum > 0 else -1)
    # MACD (12, 26, 9): Buy — main line values > signal line values, Sell — main line values < signal line values
    mainline = last(macd(close=close))
    signal = last(macd_signal(close=close))
    indicators.append(1 if mainline > signal else -1)

    # Stochastic RSI (3, 3, 14, 14): Buy — downtrend and K and D lines < 20 and K line crosses over D line, Sell — uptrend and K and D lines > 80 and K line crosses under D line
    stochrsi = StochRSIIndicator(close=close)
    k = last(stochrsi.stochrsi_k())
    d = last(stochrsi.stochrsi_d())
    trend_up = rising(close) and rising(stochrsi.stochrsi())
    trend_down = not rising(close) and not rising(stochrsi.stochrsi())
    indicators.append(
        1 if trend_down and k < 20 and d < 20 and k > d else -1 if trend_up and k > 80 and d > 80 and k < d else 0)
    # Williams %R (14): Buy — indicator < lower band and rising, Sell — indicator > upper band and falling
    williams = williams_r(high=high, low=low, close=close)
    indicators.append(
        1 if rising(williams) and last(williams) < -80 else -1 if not rising(williams) and last(williams) > -20 else 0)
    # Bulls and Bears Power: Buy — uptrend and BearPower < zero and BearPower is rising, Sell — downtrend and BullPower > zero and BullPower is falling
    # todo: add indicator
    # indicators.append(0)
    # UO (7,14,28): Buy — UO > 70, Sell — UO < 30
    uo = last(ultimate_oscillator(high=high, low=low, close=close))
    indicators.append(1 if uo > 70 else -1 if uo < 30 else 0)
    return sum(indicators) / len(indicators)


# Define stock symbol and time period
if __name__ == '__main__':
    symbol = "VORB"
    start_date = "2021-01-01"
    end_date = "2022-01-01"

    # Download historical data from Yahoo Finance
    df = yf.download(symbol, start=start_date)  # , end=end_date)
    avg = net_indicator(df)
    if avg > 0.5:
        print("Strong Buy")
    elif avg < -0.5:
        print("Strong Sell")
    elif avg < 0:
        print("Buy")
    else:
        print("Sell")
