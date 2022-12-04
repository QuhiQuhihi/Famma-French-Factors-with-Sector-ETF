import os
import sys
import pdb
import datetime

import numpy as np
import pandas as pd

import statsmodels.api as sm

from get_rawdata import RawDataGetter 
from proc_rawdata import RawDataProc

class factor_decompose:

    def __init__(self):

        rawdata = RawDataGetter()
        rawdata.run()
        self.factors = rawdata._process_factor_data()
        self.sectors = rawdata._process_sector_etf_data()
        self.year = ['2007','2008','2009','2010','2011','2011','2012','2013','2014','2015','2016','2017','2018','2019','2020','2021','2022']


    def factor_ols(self, year, ticker, factors_list):
        X = self.factors[['Mkt-RF', 'SMB','HML','RMW','CMA','Mom']]
        y = self.sectors[ticker] - self.factors['RF']
        X = sm.add_constant(X)
        ff_model = sm.OLS(y, X).fit()
        print(ff_model.summary())

        intercept, b1, b2, b3, b4, b5, b6 = ff_model.parameters
        
        rf = self.factors['RF'].mean()
        market_premium = self.factors['Mkt-RF'].mean()
        size_premium = self.factors['SMB'].mean()
        value_premium = self.factors['HML'].mean()
        robust_premium = self.factors['RMW'].mean()
        safety_premium = self.factors['CMA'].mean()
        momentum_premium = self.factors['Mom'].mean()

        expected_monthly_return = rf + b1*market_premium + b2*size_premium + b3*value_premium \
                                     + b4*robust_premium + b5*safety_premium + b6*momentum_premium

        print("Ticker is {}".format())
        print("Expected monthly Return = {}".format(expected_monthly_return))
        print("Expected Annual Return  = {}".format(expected_monthly_return*12))

        return intercept, b1, b2, b3, b4, b5, b6
    
    def run(self):
        tickers = self.sectors.columns()
        factors_list = ['Mkt-RF', 'SMB','HML','RMW','CMA','Mom']
        months = ['01','02','03']

        factor_results = pd.DataFrame(columns=factors_list, index=tickers)

        for ticker in tickers:
            intercept, b1, b2, b3, b4, b5, b6 = self.factor_ols(ticker, factors_list)
            factor_results.loc[ticker,'Mkt-RF']
            
        
        


if __name__ == '__main__':
    print("START")
    factor_decompose = factor_decompose()
    factor_decompose.run()



