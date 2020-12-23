from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
import sys
from AutoTrader_kiwoomAPI import *


#Load pyqt ui file
uiForm_class=uic.loadUiType("autoTrader_ui.ui")[0]

class TraderWindow(QMainWindow,uiForm_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        #Create kiwoom api instance 
        self.kiwoomApi=KiwoomAPI()

        #Try Login
        self.kiwoomApi.Comm_connect()

        #Create Timer(1 seconds)
        self.timer=QTimer(self)
        self.timer.start(1000) #1 second
        self.timer.timeout.connect(self.timeout_callback)

        #stock select callback
        self.UI_StockSelectLineEdit.textChanged.connect(self.StockSelect_changedCallback)

        #User account info
    
        account_count=int(self.kiwoomApi.GetLoginInfo("ACCOUNT_CNT"))
        accounts=self.kiwoomApi.GetLoginInfo("ACCNO")
        accountList=accounts.split(';')[0:account_count]
        self.UI_accountInfo.addItems(accountList)

        self.UI_OrderButton.clicked.connect(self.SendOrder)

    def timeout_callback(self):
        currentTime=QTime.currentTime()
        currentTimeStr=currentTime.toString("hh:mm:ss")
        timeMessageStr="현재시간 : {}".format(currentTimeStr)

        state=self.kiwoomApi.GetConnectState()
        if state==1:
            stateMessage="서버 연결됨"
        else:
            stateMessage="서버 미연결"
        self.statusbar.showMessage(stateMessage+" | "+timeMessageStr)

    def StockSelect_changedCallback(self):
        code=self.UI_StockSelectLineEdit.text()
        name=self.kiwoomApi.GetMasterCodeName(code)
        self.UI_StockInfoLineEdit.setText(name)
    
    def SendOrder(self):
        orderType_lookup={'신규매수':1,'신규매도':2,'매수취소':3,'매도취소':4}
        quotePrice_lookup={'지정가':'00','시장가':'03'}

        account=self.UI_accountInfo.currentText()
        orderType=orderType_lookup[self.UI_orderType.currentText()]
        code=self.UI_StockSelectLineEdit.text()
        priceType=quotePrice_lookup[self.UI_PriceTypeComboBox.currentText()]
        count=self.UI_countSpinBox.value()
        price=self.UI_PriceSpinBox.value()

        self.kiwoomApi.SendOrder("send_order_req","0101",account,orderType,code,count,price,priceType,""
        )










if __name__=="__main__":
    app=QApplication(sys.argv)
    traderWindow=TraderWindow()
    traderWindow.show()
    app.exec_()
