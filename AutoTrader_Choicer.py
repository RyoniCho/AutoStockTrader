from AutoTrader_kiwoomAPI import *
from PyQt5.QtWidgets import *
import sys


MARKET_KOSPI=0
MARKET_KOSDAQ=10


class Choicer:
    def __init__(self):
        self.kiwoomApi=KiwoomAPI()
        self.kiwoomApi.Comm_connect()
        self.GetCodeList()
        self.Run()

    def Run(self):
        print(self.kosdaqCodes[0:5])
        print(self.kospiCodes[0:5])

        
    def GetCodeList(self):
        self.kospiCodes = self.kiwoomApi.GetCodeListByMarket(MARKET_KOSPI)
        self.kosdaqCodes = self.kiwoomApi.GetCodeListByMarket(MARKET_KOSDAQ)


if __name__ == "__main__":
    app=QApplication(sys.argv)
    choicer=Choicer()
    choicer.Run()

        