from AutoTrader_kiwoomAPI import *
from PyQt5.QtWidgets import *
import sys
import time
import datetime
from pandas import DataFrame



MARKET_KOSPI=0
MARKET_KOSDAQ=10

KOSDAQ_INSIDE1000=0
KOSDAQ_OUTSIDE1000=1
KOSPI_INSIDE1000=2
KOSPI_OUTSIDE1000=3


class Choicer:
    def __init__(self):
        self.kiwoomApi=KiwoomAPI()
        self.kiwoomApi.Comm_connect()
        self.GetCodeList()
       

    def Run(self,runType):
        # df=self.GetDailyData("005935","20200103")
        # print(df)
        num = len(self.kosdaqCodes)
        print("Kospi Code count",len(self.kospiCodes))
        print("Kodaq Code count",len(self.kosdaqCodes))

        if runType==KOSDAQ_INSIDE1000:
            self.SearchSoringStock(self.kosdaqCodes,True)
        elif runType==KOSDAQ_OUTSIDE1000:
            self.SearchSoringStock(self.kosdaqCodes,False)
        elif runType==KOSPI_INSIDE1000:
            self.SearchSoringStock(self.kospiCodes,True)
        elif runType==KOSPI_OUTSIDE1000:
            self.SearchSoringStock(self.kospiCodes,False)


       

    
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
        
        todayVolume=0
        sum_volume=0

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
    def UpdateBuyList(self,buyList):
        with open("buy_list.txt","wt",encoding='utf-8') as f:
            for code in buyList:
                f.writelines("매수;{};시장가;10;0;매수전\n".format(code))
        
    def SearchSoringStock(self,codes,inside1000):
        
        buyList=list()
        num = len(codes)
        for i, code in enumerate(codes):

            if inside1000 ==False and i<1000:
                continue
                
            print(i, '/', num)
         
            if i % 99 == 0:
                print("process cool down (100)")
                time.sleep(60)
               
            if i == 999:
                print("process cool down (1000)")
                break
         

            if self.CheckSoringStock(code):
                buyList.append(code)
                print("급등주: ", code)
        
        self.UpdateBuyList(buyList)

        

       






if __name__ == "__main__":
    app=QApplication(sys.argv)
    choicer=Choicer()
    choicer.Run(KOSPI_INSIDE1000)


        