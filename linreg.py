#!/usr/local/bin/python

import numpy as np
import statsmodels.api as sm
np.random.seed(9876789)

x1 = np.array([1,2,3,4,5,6])
x2 = np.array([3,2,4,2,8,6])
x3 = np.array([2,13,5,3,2,4])
y = np.array([2,2,4,4,4,8])



nsample = 100
x = np.linspace(0, 10, 100)
X = np.column_stack((x, x**2))
beta = np.array([1, 0.1, 10])
e = np.random.normal(size=nsample)
X = sm.add_constant(X)
y = np.dot(X, beta) + e
X = sm.add_constant(X)
y = np.dot(X, beta) + e

model = sm.OLS(y, X)
results = model.fit()
print results.summary()

ind = [X[:,1], X[:,2]]
print linreg(ind, y)
# %%

def reg_m(y, x):
    ones = np.ones(len(x[0]))
    X    = sm.add_constant(np.column_stack((x[0], ones)))
    for ele in x[1:]:
        X = sm.add_constant(np.column_stack((ele, X)))
    results = sm.OLS(y, X).fit()
    return results

reg = reg_m(y, [x1, x2, x3]); reg.summary()

# %%
def linreg(X, Y):
    ''' 
    OLS linear regression
    return:
        beta, constant, r_squared, resid
    
    example:
        x1 = np.array([1,2,3,4,5,6])
        x2 = np.array([3,2,4,2,8,6])
        y  = np.array([2,2,4,4,4,8])
        
        beta, cons, r2, resid = linreg( [x1, x2, x3], y )
    '''
        
    X = np.array(X).T
    A = np.column_stack([X, np.ones(len(X))])
    result = np.linalg.lstsq( A, Y)[0]
    beta = result[:-1]; print beta
    cons = result[-1] ; print cons
    est = np.dot(X, beta) + cons
    r_squared = np.square(est - Y.mean()).sum() / np.square(Y.mean() - Y).sum()
    resid = Y - np.dot(X,beta)
    return beta, cons, r_squared, resid 

beta, cons, r_squared, resid = linreg([x1, x2, x3], y)
print 'beta =', beta, 'cons =', cons, 'r_squared =', r_squared, '\nresid =', resid

