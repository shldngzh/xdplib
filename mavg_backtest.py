#!/usr/local/bin/python
# mavg_backtest.py
# Xiaodong Zhai (xz125@duke.edu)

import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# from backtest import Strategy, Portfolio

# %% define classes

class MovingAverageCrossStrategy(object):
    '''
    Moving Average Cross Strategy
    '''
    def __init__(self, symbol, prices, win_short, win_long):
        self.symbol = symbol
        self.prices = prices
        
        self.win_short = win_short
        self.win_long = win_long

    def gen_signals(self):
        signals = pd.DataFrame(index=self.prices.index)
        signals['signal'] = 0.0
        
        signals['mavg_short'] = pd.rolling_mean(prices[symbol], self.win_short, min_periods=1)
        signals['mavg_long'] = pd.rolling_mean(prices[symbol], self.win_long, min_periods=1)
        signals['signal'][self.win_short:] = np.where(signals['mavg_short'][self.win_short:] > signals['mavg_long'][self.win_short:], 1.0, 0.0)
        signals['position'] = signals['signal'].diff()
        return signals


class MarketOnPortfolio(object):
    '''
    Portfolio
    '''
    def __init__(self, symbol, prices, signals, initial_capital=1000000.0):
        self.symbol = symbol
        self.prices = prices
        self.signals = signals
        self.initial_capital = initial_capital
        self.positions = self.gen_positions()

    def gen_positions(self):
        positions = pd.DataFrame(index=self.signals.index).fillna(0.0)
        positions[self.symbol] = 1000000 * signals['signal']
        
        return positions

    def backtest_portfolio(self):
        portfolio = self.positions * self.prices[symbol].reshape(self.positions.shape)
        
        pos_diff = self.positions.diff()
        portfolio['holdings'] = (self.positions * self.prices[symbol].reshape(self.positions.shape)).sum(axis=1)
        
        portfolio['cash'] = self.initial_capital - (pos_diff*self.prices[symbol].reshape(self.positions.shape)).sum(axis=1).cumsum()
        portfolio['total'] = portfolio['cash'] + portfolio['holdings']
        portfolio['ret'] = portfolio['total'].pct_change()
        
        return portfolio

# %%
if __name__ == '__main__':
    symbol = 'DEM'
    prices = pd.read_excel('Exchange Rates.xlsx',index_col='Pricedate')
    prices = pd.Series({'DEM':[1,2,3,4,5,6,5,4,3,4,5,6,4,3,5,6,7,9])
    
    mac = MovingAverageCrossStrategy(symbol, prices, 3, 7)
    signals = mac.gen_signals()
    
    # %% initiate portfolio
    port = MarketOnPortfolio(symbol, prices, signals, initial_capital=100000.0)
    returns = port.backtest_portfolio()

    # %% plot
    fig = plt.figure()
    fig.patch.set_facecolor('white')
    ax1 = fig.add_subplot(211,  ylabel='prices in $')
    
    # Plot the AAPL closing prices overlaid with the moving averages
    prices[symbol].plot(ax=ax1, color='r', lw=2.)
    signals[['mavg_short', 'mavg_long']].plot(ax=ax1, lw=2.)

    # Plot the "buy" trades against AAPL
    ax1.plot(signals.ix[signals.position == 1.0].index, 
             signals.mavg_short[signals.position == 1.0],
             '^', markersize=10, color='m')

    # Plot the "sell" trades against AAPL
    ax1.plot(signals.ix[signals.position == -1.0].index, 
             signals.mavg_short[signals.position == -1.0],
             'v', markersize=10, color='k')

    # Plot the equity curve in dollars
    ax2 = fig.add_subplot(212, ylabel='Portfolio value in $')
    returns['total'].plot(ax=ax2, lw=2.)

    # Plot the "buy" and "sell" trades against the equity curve
    ax2.plot(returns.ix[signals.position == 1.0].index, 
             returns.total[signals.position == 1.0],
             '^', markersize=10, color='m')
    ax2.plot(returns.ix[signals.position == -1.0].index, 
             returns.total[signals.position == -1.0],
             'v', markersize=10, color='k')

    # Plot the figure
    fig.show()
    
    
aa = pd.Series([1,2,3,4])
aa.diff()