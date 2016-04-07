#!/usr/local/bin/python
# tls.py
# Xiaodong Zhai (xz125@duke.edu)

import numpy as np
import xdzlib_alpha as xz
from scipy.odr import *
import matplotlib.pyplot as plt
from sklearn import datasets

x = diabetes_X[:, :, 2][:-20].reshape((422))

y = diabetes.target[:-20]

#x = np.array([95, 85, 80, 70, 60])
#y = np.array([85, 95, 70, 65, 70])

plt.scatter(x, y)
# %%
def f(B, x):
    '''Linear function y = m*x + b'''
    # B is a vector of the parameters.
    # x is an array of the current x values.
    # x is in the same format as the x passed to Data or RealData.
    #
    # Return an array in the same format as y passed to Data or RealData.
    return B[0]*x + B[1]
    
linear = Model(f)    
sx = x.cov()
mydata = RealData(x, y, sx=np.cov(x), sy=np.cov(y))
myodr = ODR(mydata, linear, beta0=[1., 2.])
myoutput = myodr.run()
myoutput.pprint()

# %%
result = xz.linreg_show(x,y) ; print result