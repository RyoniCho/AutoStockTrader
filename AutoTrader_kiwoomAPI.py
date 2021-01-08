from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QAxContainer import *
import sys

#키움증권 Open API를 QAxWidget클래스를 통해 인스턴스로 생성
class KiwoomAPI(QAxWidget):
    def __init__(self):
        super().__init__()
        self.Create_kiwoom_instance()
        self.SetCallback()
    
    #Set kiwoom Open API registry
    def Create_kiwoom_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")
    
    def SetCallback(self):
        self.OnEventConnect.connect(self.Callback_onEventConnect)
        self.OnReceiveTrData.connect(self.Callback_OnReceiveTradeData)
        self.OnReceiveChejanData.connect(self.AfterOrderBalanceData_Callback)


    #Login
    def Comm_connect(self):
        self.dynamicCall("CommConnect()")
        self.loginEventLoop=QEventLoop()
        self.loginEventLoop.exec_()


    def Callback_onEventConnect(self,errorCode):
        if errorCode==0:
            print("Connected")
        else:
            print("Disconnected")
        self.loginEventLoop.exit()

    def GetConnectState(self):
        return self.dynamicCall("GetConnectState()")
    
    def GetLoginInfo(self, tag):
        ret=self.dynamicCall("GetLoginInfo(Qstring)",tag)
        return ret
    
    #GetInfo: Return Stock Code Korean Name
    def GetMasterCodeName(self,code):
        codeName=self.dynamicCall("GetMasterCodeName(QString)",code)
        return codeName

    #ORDER

    def SendOrder(self,rqname,screenNo,accNo,orderType,code,quantity,price,hoga,orderNo):
        self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
        [rqname,screenNo,accNo,orderType,code,quantity,price,hoga,orderType])
    
    def GetAfterOrderBalanceData(self,fid):
        ret=self.dynamicCall("GetChejanData(int)",fid)
        return ret
    
    def AfterOrderBalanceData_Callback(self,divide,itemCount,fidList):
        #9203 주문번호
        #302 종목명
        #900 주문수량
        #901 주문가격
        #902 미체결수량 
        #904 원주문번호
        #905 주문구분
        #908 주문/체결 시간
        #909 체결가
        #911 체결량
        #10 현재가, 체결가, 실시간 종가

        print(divide)
        print(self.GetAfterOrderBalanceData(9203)) #주문번호
        print(self.GetAfterOrderBalanceData(302)) #종목명
        print(self.GetAfterOrderBalanceData(900)) #주문수량
        print(self.GetAfterOrderBalanceData(901)) #주문가격
    
    #Request Trading Data To Server (Transaction)
    #SetInputValue(TR)-> TR Request->Callback(OnReceiveTradeData)->GetData(In Callback Method)
   
    def SetInputValue(self, id, value):
        self.dynamicCall("SetInputValue(QString, QString)", id, value)

    def Comm_RequestData(self, rqname, trcode, next, screen_no):
        self.dynamicCall("CommRqData(QString, QString, int, QString)", rqname, trcode, next, screen_no)
        self.tradeData_event_loop = QEventLoop()
        self.tradeData_event_loop.exec_()
    
    def Callback_OnReceiveTradeData(self, screen_no, rqname, trcode, record_name, next, unused1, unused2, unused3, unused4):
        try:
            self.tradeData_event_loop.exit()
        except AttributeError:
            pass

    def Comm_GetData(self, code, real_type, field_name, index, item_name):
        ret = self.dynamicCall("CommGetData(QString, QString, QString, int, QString)", code, real_type, field_name, index, item_name)
        return ret.strip()
    
   
    #Get Received Data Count
    def GetRepeatCount(self, trcode, rqname):
        ret = self.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
        return ret

    #opw0001: 예수금 상세현황 요청
    def _opw00001(self, rqname, trcode):
        self.d2_deposit = self.Comm_GetData(trcode, "", rqname, 0, "d+2추정예수금")

        


