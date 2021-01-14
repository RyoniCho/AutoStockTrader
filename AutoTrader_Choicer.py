from AutoTrader_kiwoomAPI import *
from PyQt5.QtWidgets import *
import sys
import time
from pandas import DataFrame



MARKET_KOSPI=0
MARKET_KOSDAQ=10


class Choicer:
    def __init__(self):
        self.kiwoomApi=KiwoomAPI()
        self.kiwoomApi.Comm_connect()
        self.GetCodeList()
       

    def Run(self):
        df=self.GetDailyData("005935","20200103")
        print(df)

        
    def GetCodeList(self):
        self.kospiCodes = self.kiwoomApi.GetCodeListByMarket(MARKET_KOSPI)
        self.kosdaqCodes = self.kiwoomApi.GetCodeListByMarket(MARKET_KOSDAQ)

    def GetDailyData(self,code,startDate):
        self.kiwoomApi.dailyData = {'date': [], 'open': [], 'high': [], 'low': [], 'close': [], 'volume': []}

        self.kiwoomApi.SetInputValue("종목코드",code)
        self.kiwoomApi.SetInputValue("기준일자",startDate)
        self.kiwoomApi.SetInputValue("수정주가구분",1)

        self.kiwoomApi.Comm_RequestData("opt10081_rq","opt10081",0,"0101")
        time.sleep(0.2)

        df=DataFrame(self.kiwoomApi.dailyData,columns=['open','high','low','close','volume'],index=self.kiwoomApi.dailyData['date'])
        return df



if __name__ == "__main__":
    app=QApplication(sys.argv)
    choicer=Choicer()
    choicer.Run()

        