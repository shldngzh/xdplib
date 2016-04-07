#!/usr/local/bin/python
# place_order_beta.py
# Version 1.0, Beta, Jul 23 2015
# Xiaodong Zhai (xz125@duke.edu)

#%% import libraries
import gzip, os, re
import numpy
import shlex, subprocess
from scipy import c_, ones, dot, stats, diff
from scipy.linalg import inv, solve, det, norm

#%% obtain inputs and load data
inputs = raw_input ( "Inputs: hhmmhhmm 1/-1 CTw/exp. yyyymmdd lmt/mkt/stp stp-prft,stp-loss\n" ) 
#inputs = "10001330 1 ESM5 20150529 0 100,0"
orderInfo = inputs.split(" ")
timeSpan = orderInfo[0]
date = orderInfo[3]
startTime = int(date + timeSpan[0:4]+'00')
stopTime = int(date + timeSpan[4:8]+'59')
side = orderInfo[1]
product = orderInfo[2]
orderType = int(orderInfo[4])
orderStop = orderInfo[5]
orderStop_profitTicks = int(orderStop.split(",")[0])
orderStop_lossTicks = int(orderStop.split(",")[1])
#fileName = "/home/xiaodong/data/fe/eldo/1min/%s/%s/%s/eldo.%s.%s.1min.olhc.txt.gz" % (date[0:4],date[4:6],date[6:8],date,product)
fileName = "/data/fe/eldo/1min/%s/%s/%s/eldo.%s.%s.1min.olhc.txt.gz" % (date[0:4],date[4:6],date[6:8],date,product)
if not os.path.exists( fileName ): exit( fileName + " not found" )
data = numpy.loadtxt ( fileName )

# identify order type
if orderType == 0: # market order
    orderType_tag = 0 
elif orderType < 0: # limit order
    orderType_tag = -1 
    orderType_prc = -orderType
elif orderType> 0: # stop order 
    orderType_tag = 1
    orderType_prc = orderType
    
#%% roll over the time span to get raw time period index vector
i = 0
indx = []
for i in range(0,len(data)):
    if data[i,1] >= startTime and data[i,1] <= stopTime:
                indx.append(i)
                
#%% roll over the raw time period to simulate trade
i = 0
enterIndx = -1

for i in range(0,len(indx)):
    currentClosePrc = data[indx[i],6]
    # if buy side
    if side == "B" or side == "1":
        if orderType_tag == 0: # if market order
            enterIndx = 0 # buy at last close price 
            prc_enter = data[indx[enterIndx]-1,6]
        elif orderType_tag == -1: # if limit order
            if currentClosePrc <= orderType_prc and enterIndx == -1:
                enterIndx = i
                prc_enter = currentClosePrc # buy at current minute close price
        elif orderType_tag == 1: # if stop order
            if currentClosePrc >= orderType_prc and enterIndx == -1:
                enterIndx = i
                prc_enter = currentClosePrc # buy at current minute close price
    # if sell side 
    else:
        if orderType_tag == 0: # if market order
            enterIndx = i
            prc_enter = data[indx[enterIndx]-1,6]
        elif orderType_tag == -1: # if limit order
            if currentClosePrc <= orderType_prc and enterIndx == -1:
                enterIndx = i
                prc_enter = currentClosePrc
        elif orderType_tag == 1: # if stop order
            if currentClosePrc <= orderType_prc and enterIndx == -1:
                enterIndx = i
                prc_enter = currentClosePrc
    if (not enterIndx == -1) and (currentClosePrc - prc_enter >= orderStop_profitTicks) and (not orderStop_profitTicks == 0) :
        exitIndx = i;   exitTag = "Stop_Profit"
        break
    if (not enterIndx == -1) and (prc_enter - currentClosePrc >= orderStop_lossTicks) and (not orderStop_lossTicks == 0) :
        exitIndx = i;   exitTag = "Stop_Loss"
        break
    exitIndx = i;   exitTag = "Timeout"
    


indx = numpy.asanyarray(indx)        

prc_exit = data[indx[exitIndx],6]
holdPeriod = data[indx[exitIndx],1]-data[indx[enterIndx],1]

#%% 
if side == "B" or side == "1":
    PNL = prc_exit - prc_enter
    maxDraw = 1 - numpy.min(data[indx[0]:indx[-1]+1,6])/prc_enter
else:
    PNL = prc_enter - prc_exit
    maxDraw = numpy.max(data[indx[0]:indx[-1]+1,6])/prc_enter - 1
        
print "prc_enter =",prc_enter, "prc_exit =",prc_exit, exitTag,"HP =",holdPeriod, "PNL =",PNL, "MD =",maxDraw

