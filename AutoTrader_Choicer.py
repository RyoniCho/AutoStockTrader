from AutoTrader_kiwoomAPI import *
from PyQt5.QtWidgets import *
import sys
import time
import datetime
from pandas import DataFrame



MARKET_KOSPI=0
MARKET_KOSDAQ=10


class Choicer:
    def __init__(self):
        self.kiwoomApi=KiwoomAPI()
        self.kiwoomApi.Comm_connect()
        self.GetCodeList()
       

    def Run(self):
        # df=self.GetDailyData("005935","20200103")
        # print(df)

        #num = len(self.kosdaqCodes)

        for i, code in enumerate(self.kosdaqCodes):
            #print(i, '/', num)
            if self.CheckSoringStock(code):
                print("코스닥급등주: ", code)

        for code in self.kosdaqCodes:
            if self.CheckSoringStock(code):
                print("코스피급등주:",code)

        
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
    
    #급등주 체크
    def CheckSoringStock(self,code):
        today=datetime.datetime.today().strftime("%Y%m%d")
        df=self.GetDailyData(code,today)
        volumes=df['volume']
        
        #20일치 이상 필요. 예외처리
        if len(volumes)<21:
            return False
        
        for i,vol in enumerate(volumes):
            if i==0:
                todayVolume=vol
            elif 1<=i<=20:
                sum_volume+=vol
            else:
                break
        averageVolume=sum_volume/20
        #평균 거래량의 1000% 초과시
        if todayVolume>averageVolume*10:
            return True
        
        return False

        

       






if __name__ == "__main__":
    app=QApplication(sys.argv)
    choicer=Choicer()
    choicer.Run()


        