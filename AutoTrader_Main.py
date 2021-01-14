from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
import sys
from AutoTrader_kiwoomAPI import *
import time

import os
#Load pyqt ui file

uiForm_class=uic.loadUiType("AutoTrader/autoTrader_ui.ui")[0]

class TraderWindow(QMainWindow,uiForm_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.autoTradeOrderDone=False

        #Create kiwoom api instance 
        self.kiwoomApi=KiwoomAPI()

        #Try Login
        self.kiwoomApi.Comm_connect()

        #Create Timer(1 seconds)
        self.timer=QTimer(self)
        self.timer.start(1000) #1 second
        self.timer.timeout.connect(self.timeout_callback)

        # Timer2
        self.timer2 = QTimer(self)
        self.timer2.start(1000*10) #10 second
        self.timer2.timeout.connect(self.timeout2_callback)

        #stock select callback
        self.UI_StockSelectLineEdit.textChanged.connect(self.StockSelect_changedCallback)

        #User account info
    
        account_count=int(self.kiwoomApi.GetLoginInfo("ACCOUNT_CNT"))
        accounts=self.kiwoomApi.GetLoginInfo("ACCNO")
        accountList=accounts.split(';')[0:account_count]
        self.UI_accountInfo.addItems(accountList)
        
        #set call back
        self.UI_OrderButton.clicked.connect(self.SendOrder)
        self.UI_checkBalance_pushButton.clicked.connect(self.CheckBalance)

        #Load AutoStock List
        self.Load_AutoStockList()

    def timeout_callback(self):
        marketStartTime = QTime(9, 0, 0)
        currentTime=QTime.currentTime()
        
        if currentTime > marketStartTime and self.autoTradeOrderDone is False:
            self.AutoStockOrder()
            self.autoTradeOrderDone = True
        
        currentTimeStr=currentTime.toString("hh:mm:ss")
        timeMessageStr="현재시간 : {}".format(currentTimeStr)

        state=self.kiwoomApi.GetConnectState()
        if state==1:
            stateMessage="서버 연결됨"
        else:
            stateMessage="서버 미연결"
        self.statusbar.showMessage(stateMessage+" | "+timeMessageStr)

    def timeout2_callback(self):
        if self.UI_realTimeBalance_checkBox.isChecked():
            self.CheckBalance()


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

        self.kiwoomApi.SendOrder("send_order_req","0101",account,orderType,code,count,price,priceType,"")
    
    def CheckBalance(self):
        self.kiwoomApi.Reset_opw00018_output()

        account_number = self.kiwoomApi.GetLoginInfo("ACCNO")
        account_number = account_number.split(';')[0]
        #opw00018(계좌평가 잔고내역)
        self.kiwoomApi.SetInputValue("계좌번호", account_number)
        self.kiwoomApi.Comm_RequestData("opw00018_req", "opw00018", 0, "2000")

        while self.kiwoomApi.remained_data:
            time.sleep(0.2)
            self.kiwoomApi.SetInputValue("계좌번호", account_number)
            self.kiwoomApi.Comm_RequestData("opw00018_req", "opw00018", 2, "2000")
        
        # opw00001 (예수금내역)
        self.kiwoomApi.SetInputValue("계좌번호", account_number)
        self.kiwoomApi.Comm_RequestData("opw00001_req", "opw00001", 0, "2000")


        # Set Deposit UI (예수금)
        item = QTableWidgetItem(self.kiwoomApi.d2_deposit)
        item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
        self.UI_deposit_tableWidget.setItem(0, 0, item)

        for i in range(1, 6):
            item = QTableWidgetItem(self.kiwoomApi.opw00018_output['single'][i - 1])
            item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            self.UI_deposit_tableWidget.setItem(0, i, item)

        self.UI_deposit_tableWidget.resizeRowsToContents()

        # Set Balance UI (계좌평가잔고내역)
        item_count = len(self.kiwoomApi.opw00018_output['multi'])
        self.UI_balance_tableWidget.setRowCount(item_count)
        print("00018:{}".format(item_count))

        for j in range(item_count):
            row = self.kiwoomApi.opw00018_output['multi'][j]
            for i in range(len(row)):
                item = QTableWidgetItem(row[i])
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
                self.UI_balance_tableWidget.setItem(j, i, item)

        self.UI_balance_tableWidget.resizeRowsToContents()

    def Load_AutoStockList(self):
        f = open("AutoTrader/buy_list.txt", 'rt',encoding='utf-8')
        buy_list = f.readlines()
        f.close()

        f = open("AutoTrader/sell_list.txt", 'rt',encoding='utf-8')
        sell_list = f.readlines()
        f.close()

        row_count = len(buy_list) + len(sell_list)
        self.UI_autoSelectStock_tableWidget.setRowCount(row_count)

        # buy list
        for j in range(len(buy_list)):
            row_data = buy_list[j]
            split_row_data = row_data.split(';')
            split_row_data[1] = self.kiwoomApi.GetMasterCodeName(split_row_data[1].rsplit())

            for i in range(len(split_row_data)):
                item = QTableWidgetItem(split_row_data[i].rstrip())
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignCenter)
                self.UI_autoSelectStock_tableWidget.setItem(j, i, item)

        # sell list
        for j in range(len(sell_list)):
            row_data = sell_list[j]
            split_row_data = row_data.split(';')
            split_row_data[1] = self.kiwoomApi.GetMasterCodeName(split_row_data[1].rstrip())

            for i in range(len(split_row_data)):
                item = QTableWidgetItem(split_row_data[i].rstrip())
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignCenter)
                self.UI_autoSelectStock_tableWidget.setItem(len(buy_list) + j, i, item)

        self.UI_autoSelectStock_tableWidget.resizeRowsToContents()

    def AutoStockOrder(self):
        hoga_lookup = {'지정가': "00", '시장가': "03"}

        f = open("AutoTrader/buy_list.txt", 'rt',encoding='utf-8')
        buy_list = f.readlines()
        f.close()

        f = open("AutoTrader/sell_list.txt", 'rt',encoding='utf-8')
        sell_list = f.readlines()
        f.close()

        # account
        account = self.UI_accountInfo.currentText()

        # buy list
        for row_data in buy_list:
            split_row_data = row_data.split(';')
            hoga = split_row_data[2]
            code = split_row_data[1]
            num = split_row_data[3]
            price = split_row_data[4]

            if split_row_data[-1].rstrip() == '매수전':
                self.kiwoomApi.SendOrder("send_order_req", "0101", account, 1, code, num, price, hoga_lookup[hoga], "")

        # sell list
        for row_data in sell_list:
            split_row_data = row_data.split(';')
            hoga = split_row_data[2]
            code = split_row_data[1]
            num = split_row_data[3]
            price = split_row_data[4]

            if split_row_data[-1].rstrip() == '매도전':
                self.kiwoomApi.SendOrder("send_order_req", "0101", account, 2, code, num, price,hoga_lookup[hoga], "")

        # buy list
        for i, row_data in enumerate(buy_list):
            buy_list[i] = buy_list[i].replace("매수전", "주문완료")

        # file update
        f = open("buy_list.txt", 'wt',encoding='utf-8')
        for row_data in buy_list:
            f.write(row_data)
        f.close()

        # sell list
        for i, row_data in enumerate(sell_list):
            sell_list[i] = sell_list[i].replace("매도전", "주문완료")

        # file update
        f = open("sell_list.txt", 'wt',encoding='utf-8')
        for row_data in sell_list:
            f.write(row_data)
        f.close()











if __name__=="__main__":
    app=QApplication(sys.argv)
    traderWindow=TraderWindow()
    traderWindow.show()
    app.exec_()
   







