import os
import sys
import pdb
import datetime

import numpy as np
import pandas as pd

# from pandas_datareader import data as pdr
import yfinance as yf
# yf.pdr_override()

from zipfile import ZipFile
from io import BytesIO
from urllib.request import urlopen

class RawDataGetter:


    def __init__(self):


        self.today = datetime.datetime.today()
        self.today_str = self.today.strftime('%Y-%m-%d')

        self.START_DATE = pd.Timestamp('2007-01-03')
        self.END_DATE = pd.Timestamp('2022-12-01')

        self.main_dir = os.getcwd()
        self.data_dir = os.path.join(self.main_dir, 'data',self.today_str)

        self.universe = [
            "IYW", # iShares U.S. Technology ETF|2000-05-15|
            "IYF", # iShares U.S. Financials ETF|2000-05-22|
            "IYZ", # iShares U.S. Telecommunications ETF|2000-05-22|
            "IYH", # iShares U.S. Healthcare ETF|2000-06-12|
            "IYE", # iShares U.S. Energy ETF|2000-06-12|
            "IYK", # iShares U.S. Consumer Staples ETF|2000-06-12|
            "IYG", # iShares U.S. Financial Services ETF|2000-06-12|
            "IYJ", # iShares U.S. Industrials ETF|2000-06-12|
            "IDU", # iShares U.S. Utilities ETF|2000-06-12|
            "IYM", # iShares U.S. Basic Materials ETF|2000-06-12|
            "IYC", # iShares U.S. Consumer Discretionary ETF|2000-06-12|
            "IBB", # iShares Biotechnology ETF|2001-02-05|
            "IGM", # iShares Expanded Tech Sector ETF|2001-03-13|
            "SOXX", # iShares Semiconductor ETF|2001-07-10|
            "IGV", # iShares Expanded Tech-Software Sector ETF|2001-07-10|
            "IGN", # iShares North American Tech-Multimedia Networking ETF|2001-07-10|
            "IGE", # iShares North American Natural Resources ETF|2001-10-22|
            "IYT", # iShares U.S. Transportation ETF|2003-10-06|
            "IHI", # iShares U.S. Medical Devices ETF|2006-05-01|
            "ITA", # iShares U.S. Aerospace & Defense ETF|2006-05-01|
            "IHF", # iShares U.S. Healthcare Providers ETF|2006-05-01|
            "IEO", # iShares U.S. Oil & Gas Exploration & Production ETF|2006-05-01|
            "ITB", # iShares U.S. Home Construction ETF|2006-05-01|
            "IAT", # iShares U.S. Regional Banks ETF|2006-05-01|
            "IAI", # iShares U.S. Broker-Dealers & Securities Exchanges ETF|2006-05-01|
            "IAK", # iShares U.S. Insurance ETF|2006-05-01|
            "IHE", # iShares U.S. Pharmaceuticals ETF|2006-05-01|
            "IEZ"  # iShares U.S. Oil Equipment & Services ETF|2006-05-01|
                ]


    def get_market_date(self):

        # Get Monthly sector ETF data from yahoo finance
        # mkt_data = yf.download(self.universe, start=self.START_DATE,interval="1mo")['Adj Close']

        # Get Daily sector ETF data from yahoo finance
        mkt_data = yf.download(self.universe, start=self.START_DATE, interval="1d")['Adj Close']

        mkt_data.to_csv(os.path.join(self.data_dir,'sector_ETF.csv'))

        return mkt_data


        # first_date_data = mkt_data.iloc[0:1]
        # mkt_data_m = mkt_data.resample('M').last()

        # # mkt_data = mkt_data.concat(first_date_data)
        # mkt_data = pd.concat([mkt_data_m,first_date_data])
        # mkt_data.sort_index(inplace=True)

        # mkt_data = mkt_data.ffill()
        # mkt_data = 1+np.log(mkt_data/mkt_data.shift(1))
        # mkt_data = mkt_data.fillna(1)
        # mkt_data.index = mkt_data.index.strftime('%Y%m%d')
        # mkt_data = mkt_data.loc[
        #     self.START_DATE.strftime('%Y%m%d'):self.END_DATE.strftime('%Y%m%d')
        # ]
        # # print(mkt_data)

        # mkt_data.to_csv(os.path.join(self.data_dir,'sector_ETF.csv'))

        # return mkt_data
    
    def get_fama_french_data(self):

        # Daily data
        # Fama-French 5 Factor (MKT-RF, SMB, HML, RMW, CMA)
        # url = \
        #     "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/" + \
        #     "F-F_Research_Data_5_Factors_2x3_daily_CSV.zip"
        # file_name = "F-F_Research_Data_5_Factors_2x3_daily.CSV"

        # df_ff5 = pd.read_csv(file, index_col=0, skiprows=3)
        # df_ff5 = df_ff5.loc[
        #     self.START_DATE.strftime('%Y%m%d'):self.END_DATE.strftime('%Y%m%d')
        # ]

        # Momentum Factor        
        # url = \
        #     "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/" + \
        #     "F-F_Momentum_Factor_daily_CSV.zip"
        # file_name = "F-F_Momentum_Factor_daily.CSV"
        # file = self.get_file_from_url(url, file_name)

        # df_mom = pd.read_csv(file, index_col=0, skiprows=13).iloc[:-1]
        # df_mom = df_mom.loc[
        #     self.START_DATE.strftime('%Y%m%d'):self.END_DATE.strftime('%Y%m%d')
        # ]

        # Monthly Data
        url = \
            "http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/" + \
            "F-F_Research_Data_5_Factors_2x3_CSV.zip"
        file_name = "F-F_Research_Data_5_Factors_2x3.csv"
        file = self.get_file_from_url(url, file_name)
        df_ff5 = pd.read_csv(file, index_col=0, skiprows=3)
        df_ff5 = df_ff5.loc[
            self.START_DATE.strftime('%Y%m'):
        ]


        url = \
            "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/" + \
            "F-F_Momentum_Factor_CSV.zip"
        file_name = "F-F_Momentum_Factor.CSV"
        file = self.get_file_from_url(url, file_name)
        df_mom = pd.read_csv(file, index_col=0, skiprows=13).iloc[:-1]
        df_mom = df_mom.loc[
            self.START_DATE.strftime('%Y%m'):
        ]

        # save factor data to csv
        save_factor_data = True
        if save_factor_data == True and os.path.exists(self.data_dir) == False:
            os.mkdir(self.data_dir)
            df_ff5.to_csv(os.path.join(self.data_dir, "F-F_Research_Data_5_Factors_2x3.CSV"))
            df_mom.to_csv(os.path.join(self.data_dir, "F-F_Momentum_Factor.CSV"))
        elif save_factor_data == True and os.path.exists(self.data_dir) == True:
            df_ff5.to_csv(os.path.join(self.data_dir, "F-F_Research_Data_5_Factors_2x3.CSV"))
            df_mom.to_csv(os.path.join(self.data_dir, "F-F_Momentum_Factor.CSV"))
        else:
            pass
        return df_ff5, df_mom

    def get_file_from_url(self, url, file_name):

        r = urlopen(url).read()
        file = ZipFile(BytesIO(r))
        file = file.open(file_name)

        return file
    
    def run(self):
        self.get_fama_french_data()
        self.get_market_date()
        

if __name__ == '__main__':
    print("START")

    rawdata = RawDataGetter()
    rawdata.run()

    # rawdata.get_fama_french_data()
    # rawdata.get_market_date()
    # pdb.set_trace()

