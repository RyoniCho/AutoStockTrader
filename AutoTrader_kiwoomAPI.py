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
        #연속된 데이터가 더 있는지 확인
        if next=='2':
            self.remained_data=True
        else:
            self.remained_data=False
        #리퀘스트 종류에 따른 처리
        if rqname =="opt10081_rq":
            self._opt10081(rqname,trcode)
        elif rqname == "opw00001_req":
            self._opw00001(rqname, trcode)
        elif rqname == "opw00018_req":
            self._opw00018(rqname, trcode)
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

    #Util: 왼쪽0 제거 및 천자리 쉼표 추가.
    @staticmethod
    def ChangeFormat(data):
        strip_data = data.lstrip('-0')
        if strip_data == '':
            strip_data = '0'

        try:
            format_data = format(int(strip_data), ',d')
        except:
            format_data = format(float(strip_data))

        if data.startswith('-'):
            format_data = '-' + format_data

        return format_data
    @staticmethod
    def ChangeFormat2(data):
        strip_data = data.lstrip('-0')

        if strip_data == '':
            strip_data = '0'

        if strip_data.startswith('.'):
            strip_data = '0' + strip_data

        if data.startswith('-'):
            strip_data = '-' + strip_data

        return strip_data
    
    #opw0001: 예수금 상세현황 요청->이에 대한 처리
    def _opw00001(self, rqname, trcode):
        d2_deposit = self.Comm_GetData(trcode, "", rqname, 0, "d+2추정예수금")
        self.d2_deposit = KiwoomAPI.ChangeFormat(d2_deposit)

    #opt10081: 주식 일봉 차트 조회 요청(여러개의 데이터들어옴)->이에 대한 처리
    def _opt10081(self,rqname,trcode):
        dataCount=self.GetRepeatCount(trcode,rqname)

        for i in range(dataCount):
            date=self.Comm_GetData(trcode,"",rqname,i,"일자")
            open=self.Comm_GetData(trcode,"",rqname,i,"시가")
            high=self.Comm_GetData(trcode,"",rqname,i,"고가")
            low = self.Comm_GetData(trcode, "", rqname, i, "저가")
            close = self.Comm_GetData(trcode, "", rqname, i, "현재가")
            volume = self.Comm_GetData(trcode, "", rqname, i, "거래량")
            print(date, open, high, low, close, volume)

    #opw00018: 계좌평가잔고내역 요청->이에 대한 처리
    def _opw00018(self, rqname,trcode):
        total_purchase_price = self.Comm_GetData(trcode, "", rqname, 0, "총매입금액")
        total_eval_price = self.Comm_GetData(trcode, "", rqname, 0, "총평가금액")
        total_eval_profit_loss_price = self.Comm_GetData(trcode, "", rqname, 0, "총평가손익금액")
        total_earning_rate = self.Comm_GetData(trcode, "", rqname, 0, "총수익률(%)")
        estimated_deposit = self.Comm_GetData(trcode, "", rqname, 0, "추정예탁자산")

        # print(KiwoomAPI.ChangeFormat(total_purchase_price))
        # print(KiwoomAPI.ChangeFormat(total_eval_price))
        # print(KiwoomAPI.ChangeFormat(total_eval_profit_loss_price))
        # print(KiwoomAPI.ChangeFormat(total_earning_rate))
        # print(KiwoomAPI.ChangeFormat(estimated_deposit))

        self.opw00018_output['single'].append(KiwoomAPI.ChangeFormat(total_purchase_price))
        self.opw00018_output['single'].append(KiwoomAPI.ChangeFormat(total_eval_price))
        self.opw00018_output['single'].append(KiwoomAPI.ChangeFormat(total_eval_profit_loss_price))
      

        total_earning_rate = KiwoomAPI.ChangeFormat(total_earning_rate)

        #모의투자일경우의 처리
        if self.GetCurrentServerType():
            total_earning_rate = float(total_earning_rate) / 100
            total_earning_rate = str(total_earning_rate)

        self.opw00018_output['single'].append(total_earning_rate)
        self.opw00018_output['single'].append(KiwoomAPI.ChangeFormat(estimated_deposit))
        

        #multi data
        rows=self.GetRepeatCount(trcode,rqname)
        for i in range(rows):
            name=self.Comm_GetData(trcode,"",rqname,i,"종목명")
            quantity=self.Comm_GetData(trcode,"",rqname,i,"보유수량")
            purchase_price = self.Comm_GetData(trcode, "", rqname, i, "매입가")
            current_price = self.Comm_GetData(trcode, "", rqname, i, "현재가")
            eval_profit_loss_price = self.Comm_GetData(trcode, "", rqname, i, "평가손익")
            earning_rate = self.Comm_GetData(trcode, "", rqname, i, "수익률(%)")

            quantity = KiwoomAPI.ChangeFormat(quantity)
            purchase_price = KiwoomAPI.ChangeFormat(purchase_price)
            current_price = KiwoomAPI.ChangeFormat(current_price)
            eval_profit_loss_price = KiwoomAPI.ChangeFormat(eval_profit_loss_price)
            earning_rate = KiwoomAPI.ChangeFormat2(earning_rate)

            self.opw00018_output['multi'].append([name, quantity, purchase_price, current_price,eval_profit_loss_price, earning_rate])
    
    def Reset_opw00018_output(self):
        self.opw00018_output = {'single': [], 'multi': []}
    
    def GetCurrentServerType(self):
        ret = self.dynamicCall("KOA_Functions(QString, QString)", "GetServerGubun", "")
        return ret
            
            

        







