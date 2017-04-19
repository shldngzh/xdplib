#!/usr/local/bin/python
# key_reversal.py
# Python2.7
# Version 2.8.2 Alpha, Jul 9 2015
#   New method to get inputs, simpler code and neat
# Version 2.8.1 Alpha, Jul 9 2015
#   Added the default time span to run the whole day dataset
# Version 2.8 Alpha, Jul 8 2015

# Xiaodong Zhai (xz125@duke.edu)

import numpy as np
import xdzlib_beta as xz

class TradeRecord(object):

    def __init__(self):
        """
        initiate the class TradeRecord, with 2 attributes:
            1) record, to record all the trades
            2) pnl, according to record to compute P&L
        """
        self.record = np.array([0, 0, 0, 0, 0])
        self.pnl = np.ndarray([])
        return None

    def get_record(self, epoch, time, pos_tag, position, prc):
        self.record = np.vstack((self.record, [epoch, time, pos_tag, position, prc]))
        return None

    def finalize_record(self):
        self.record = self.record[1:]
        return None

    def display_record(self):
        print self.record
        return None

    def get_stats(self):
        # number of trades
        num_of_trades = self.record.shape[0] / 2
        # number of profit_lock_out
        num_of_profitlock = np.count_nonzero(np.where(self.record[:,2] == "profit_lock_out"))
        # number of stop_out
        num_of_stopout = np.count_nonzero(np.where(self.record[:,2] == "trailing_stop_out" ))
        num_of_stopout += np.count_nonzero(np.where(self.record[:,2] == "hard_stop_out" ))
        # number of reversed_out
        num_of_reversed_out = np.count_nonzero(np.where(self.record[:,2] == "reversed_out"))
        # number of time_out
        num_of_time_out = np.count_nonzero(np.where(self.record[:,2] == "time_out"))
        # PNL
        i = 1
        for i in range(1, num_of_trades * 2, 2):
            if self.record[i, 3] == "long":
                self.pnl = np.append(self.pnl,float(self.record[i,4])-float(self.record[i-1,4]))
            elif self.record[i, 3] == "short":
                self.pnl = np.append(self.pnl,float(self.record[i-1,4])-float(self.record[i,4]))
        lst.pnl = lst.pnl[1:]
        # output statistical results
        print "# trades", num_of_trades, "# profit_lock", num_of_profitlock,\
              "# stopout", num_of_stopout, "# reversed_out",\
              num_of_reversed_out, "# time_out", num_of_time_out
        print "P&L Summary Stats:", lst.pnl.__len__(), lst.pnl.mean()/tickBase, lst.pnl.std()/tickBase, lst.pnl.min()/tickBase, lst.pnl.max()/tickBase
              
         
# %% read data and setup initial parameters
#inputs = raw_input("Inputs:Product hhmm,hhmm(0,0 for whole dataset) yyyymmdd prft_stp,+lss_stp/-trail_stop\n")
inputs = "ESM5 0600,1700 20150529 5,-8"
product, time_span, date, stop_ticks = inputs.split(' ')
time_span_start = time_span.split(',')[0]
time_span_end = time_span.split(',')[1]
pt = float(stop_ticks.split(",")[0])
tt = float(stop_ticks.split(",")[1])

fileName = "C:\cygwin64\home\Trader\Dev\eldo\data\eldo.20150529.ESM5.1min.olhc.txt.gz"
bars = np.loadtxt(fileName)
#bars = xz.get_data('GCM5','20150401', '20150501')

tickBase = 25
profit_lock = pt * tickBase
trailing_tick = tt * tickBase

lst = TradeRecord()


# %% roll over the data
#i = 1
position = 0
indx_start_of_trade = -1

for i in range(0, len(bars)):
    current_epoch = bars[i, 0]
    current_time = bars[i, 1]
    current_open = bars[i, 3]
    current_low = bars[i, 4]
    current_high = bars[i, 5]
    current_close = bars[i, 6]
    last_open = bars[i - 1, 3]
    last_low = int(bars[i - 1, 4])
    last_high = int(bars[i - 1, 5])
    last_close = int(bars[i - 1, 6])
    
    # trailing stop out
    if tt < 0:  
        if position == 1 and np.max(bars[indx_start_of_trade:i,5]) - abs(trailing_tick) > current_low:
            lst.get_record(current_epoch, current_time, 'trailing_stop_out', 
                           'long',np.minimum(current_open,last_high+trailing_tick))
            position = 0
            next
            
        if position == -1 and np.min(bars[indx_start_of_trade:i,4]) + abs(trailing_tick) < current_high:
            lst.get_record(current_epoch, current_time, 'trailing_stop_out', 
                           'short',np.maximum(current_open,last_low-trailing_tick))
            position = 0
            next
    # hard stop out
    if tt > 0:
        if position == 1 and last_high - trailing_tick >= current_low:
            lst.get_record(current_epoch, current_time, 'hard_stop_out', 
                           'long',np.minimum(current_open,last_high-trailing_tick))
            position = 0
            next
            
        if position == -1 and last_low + trailing_tick <= current_high:
            lst.get_record(current_epoch, current_time, 'hard_stop_out', 
                           'short',np.maximum(current_open,last_low+trailing_tick))
            position = 0
            next
        
    # profit [static] lock out
    if position == 1 and float(lst.record[-1,4]) + profit_lock <= current_high:
        prc_enter = float(lst.record[-1, 4])
        lst.get_record(current_epoch,current_time,
                       'profit_lock_out', 'long',
                       np.maximum(current_open, prc_enter + profit_lock))
        position = 0
        next
    elif position == -1 and float(lst.record[-1,4]) - profit_lock >= current_low:
        prc_enter = float(lst.record[-1, 4])
        lst.get_record(current_epoch, current_time, 
                       'profit_lock_out', 'short',
                       np.minimum(current_open, prc_enter - profit_lock))
        position = 0
        next


    # timeout
    if position == 1 and current_epoch == bars[-1, 0]:
        lst.get_record(current_epoch,current_time,'time_out',"long",current_close)
        position = 0
    elif position == -1 and current_epoch == bars[-1, 0]:
        lst.get_record(current_epoch,current_time,'time_out',"short",current_close)
        position = 0

    # down-trend reversing to up-trend, to LONG
    if current_open < last_close and current_close > last_high:
        if position == 0:
            lst.get_record(current_epoch,current_time,'enter','long',current_close)
            position = 1
            indx_start_of_trade = i
            next
        elif position == 1:
            position = 1
            indx_start_of_trade = i
            next
        elif position == -1:
            lst.get_record(current_epoch,current_time,'reversed_out','short',current_close)
            lst.get_record(current_epoch,current_time,'enter','long',current_close)
            position = 1
            indx_start_of_trade = i
            next
    # up-trend reversing to down-trend, to SHORT
    if current_open > last_close and current_close < last_low:
        if position == 0: 
            lst.get_record(current_epoch,current_time,'enter','short',current_close)  # enter
            position = -1
            indx_start_of_trade = i
            next
        elif position == 1:
            lst.get_record(current_epoch,current_time,'reversed_out','long',current_close)  # exit
            lst.get_record(current_epoch,current_time,'enter','short',current_close)  # enter
            position = -1
            indx_start_of_trade = i
            next
        elif position == -1:
            position = -1  # keep short position
            next


# %% results
lst.finalize_record()
lst.display_record()
lst.get_stats()
#
#a = stats.describe(lst.pnl/tickBase)
#print a

# %%
#plt.figure()
#plt.scatter(np.arange(0,len(lst.pnl)),lst.pnl)
#plt.ylim([-300,300])
#plt.figure()
#plt.hist(lst.pnl/tickBase,bins=20)

# %%


