import os
import sys
import pdb
import datetime

import numpy as np
import pandas as pd

import statsmodels.api as sm

# from get_rawdata import RawDataGetter 
# from proc_rawdata import RawDataProc

class FactorDecompose:

    def __init__(self):


        self.today = datetime.datetime.today()
        self.today_str = self.today.strftime('%Y-%m-%d')
        self.main_dir = os.getcwd()
        self.data_dir = os.path.join(self.main_dir, 'data',self.today_str)

        self.factors = pd.read_csv(os.path.join(self.data_dir, 'factor_data.csv'), index_col=0)
        self.sectors = pd.read_csv(os.path.join(self.data_dir, 'sector_data.csv'), index_col=0)
        
        self.years = ['2007','2008','2009','2010','2011','2011','2012','2013','2014','2015','2016','2017','2018','2019','2020','2021','2022']
        self.months = ['01','02','03','04','05','06','07','08','09','10','11','12']


    
    def factor_ols(self, year, ticker, factors_list):
        # select columns for factor data
        rf_data = self.factors[['RF']]
        factor_data = self.factors[['Mkt-RF', 'SMB','HML','RMW','CMA','Mom']]
        sector_data = self.sectors[ticker] - self.factors['RF'] -1

        if year != '2022':
            date_index = []
            for month in self.months:
                date_index.append(int(year+month))
        else:
            date_index = []
            months = ['01','02','03','04','05','06','07','08','09','10']
            for month in months:
                date_index.append(int(year+month))  

        rf_data = rf_data.loc[date_index]
        factor_data = factor_data.loc[date_index]
        sector_data = sector_data.loc[date_index]

        X = factor_data
        y = sector_data

        """
        /lib/python3.8/site-packages/scipy/stats/_stats_py.py:1772: UserWarning: kurtosistest only valid for n>=20 
        ... continuing anyway, n=12
        this warning message happened. I will change it to daily return later
        """

        X = sm.add_constant(X)
        ff_model = sm.OLS(y, X).fit()
        # print(ff_model.summary())

        intercept, b1, b2, b3, b4, b5, b6 = ff_model.params
        
        rf = rf_data['RF'].mean()
        market_premium = factor_data['Mkt-RF'].mean()
        size_premium = factor_data['SMB'].mean()
        value_premium = factor_data['HML'].mean()
        robust_premium = factor_data['RMW'].mean()
        safety_premium = factor_data['CMA'].mean()
        momentum_premium = factor_data['Mom'].mean()

        expected_monthly_return = rf + b1*market_premium + b2*size_premium + b3*value_premium \
                                     + b4*robust_premium + b5*safety_premium + b6*momentum_premium

        print("Ticker is {}".format(ticker))
        print("Expected monthly Return = {}".format(expected_monthly_return))
        print("Expected Annual Return  = {}".format(expected_monthly_return*12))

        return intercept, b1, b2, b3, b4, b5, b6
    
    def run(self):
        tickers = self.sectors.columns
        factors_list = ['Mkt-RF', 'SMB','HML','RMW','CMA','Mom']
        df_column = ['id','ticker','year','Mkt-RF', 'SMB','HML','RMW','CMA','Mom']

        factor_results = pd.DataFrame(columns=df_column)
        factor_results.set_index('id', inplace=True)

        i = 0
        for year in self.years:
            for ticker in tickers:
                factor_append = pd.DataFrame(columns=df_column)
                factor_append.set_index('id', inplace=True)

                intercept, b1, b2, b3, b4, b5, b6 = self.factor_ols(year, ticker, factors_list)

                factor_append.loc[i,'ticker'] = ticker
                factor_append.loc[i,'year'] = year
                factor_append.loc[i,'Mkt-RF'] = b1
                factor_append.loc[i,'SMB'] = b2
                factor_append.loc[i,'HML'] = b3
                factor_append.loc[i,'RMW'] = b4
                factor_append.loc[i,'CMA'] = b5
                factor_append.loc[i,'Mom'] = b6
                print(factor_append)
                factor_results = pd.concat([factor_results,factor_append], axis=0)
                i=i+1
        
        return factor_results
    
        
        


if __name__ == '__main__':
    print("START")
    factor_decompose = factor_decompose()
    factor_decompose.run()


