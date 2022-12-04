import os
import sys
import pdb
import datetime

import numpy as np
import pandas as pd

class RawDataProc:
    def __init__(self):

        self.today = datetime.datetime.today()
        self.today_str = self.today.strftime('%Y-%m-%d')
        self.START_DATE = pd.Timestamp('2007-01-01')
        self.END_DATE = pd.Timestamp(self.today)

        self.main_dir = os.getcwd()
        self.data_dir = os.path.join(self.main_dir, 'data',self.today_str)
    
        self.ff5_data = pd.read_csv(
            os.path.join(self.data_dir, 'F-F_Research_Data_5_Factors_2x3.csv') ,index_col=0
        )
        self.mom_data = pd.read_csv(
            os.path.join(self.data_dir, 'F-F_Momentum_Factor.CSV') ,index_col=0
        )
        self.sector_etf_data = pd.read_csv(
            os.path.join(self.data_dir, 'sector_ETF.csv'), index_col='Date', parse_dates=True
        )

    
    def _process_sector_etf_data(self):
        mkt_data = self.sector_etf_data
        first_date_data = mkt_data.iloc[0:1]
        mkt_data_m = mkt_data.resample('M').last()

        mkt_data = pd.concat([mkt_data_m,first_date_data])
        mkt_data.sort_index(inplace=True)

        mkt_data = mkt_data.ffill()
        mkt_data = 1+np.log(mkt_data/mkt_data.shift(1))
        mkt_data = mkt_data.fillna(1)
        # mkt_data.index = mkt_data.index.strftime('%Y%m%d')
        # mkt_data = mkt_data.loc[
        #     self.START_DATE.strftime('%Y%m%d') : self.END_DATE.strftime('%Y%m%d')
        # ]

        mkt_data.index = mkt_data.index.strftime('%Y%m%d')
        mkt_data = mkt_data.loc[
            self.START_DATE.strftime('%Y%m%d') : self.END_DATE.strftime('%Y%m%d')
        ]

        # mkt_data.index = mkt_data.index.strftime('%Y%m')
        mkt_data = mkt_data.iloc[1:]

        mkt_data.index = pd.to_datetime(mkt_data.index)
        mkt_data.index = mkt_data.index.strftime('%Y%m')

        # mkt_data.to_csv(os.path.join(self.data_dir,'sector_data.csv'))

        print(mkt_data)
        return mkt_data

    def _process_factor_data(self):


        ff5_data = self.ff5_data.loc[: ' Annual Factors: January-December ']
        mom_data = self.mom_data.loc[:'Annual Factors:']

        # ff5_data.index = pd.to_datetime(ff5_data.index)
        # mom_data.index = pd.to_datetime(mom_data.index)

        factor = pd.concat([ff5_data.iloc[:-1], mom_data.iloc[:-1]], axis=1)

        return factor
    
    def run(self):
        sector_data = self._process_sector_etf_data()
        factor_data = self._process_factor_data() 

        return sector_data, factor_data

if __name__ == '__main__':
    print("START")
    rawdataproc = RawDataProc()
    rawdataproc.run()

    

