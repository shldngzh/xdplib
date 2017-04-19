import statsmodels.api as sm

Y = ;
X = sm.add_constant(X)

model = sm.OLS(Y, X)
result = model.fit()

print(result.summary())

residual = result.resid
params = result.params
