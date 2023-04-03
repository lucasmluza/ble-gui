import sys
import simplepyble
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow

from threading import *

from time import sleep
from datetime import datetime

from main_ui import Ui_Dialog

UUID_SPS = "2456e1b9-26e2-8f83-e744-f34f01e9d701"
UUID_FIFO = "2456e1b9-26e2-8f83-e744-f34f01e9d703"


class Window(QMainWindow, Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowIcon(QtGui.QIcon('logo.png'))

        self.adapter = simplepyble.Adapter.get_adapters()[0]

        self.setupUi(self)
        self.pushButton_scan.clicked.connect(lambda : self.thread(self.adapter))
        self.pushButton_connect.clicked.connect(self.connect)
        self.pushButton_exit.clicked.connect(self.exit)
        self.pushButton_clear.clicked.connect(self.clear)

        self.target_peripheral = {}

    def thread(self, adapter):
        thread_scan = Thread(target=self.scan, args=[adapter])
        thread_progress = Thread(target=self.progress)
        thread_scan.start()
        thread_progress.start()

    def progress(self):
        for i in range(100):
            sleep(0.1)
            self.progressBar.setValue(i+1)
        sleep(0.1)
        self.progressBar.setValue(0)

    def scan(self, adapter):
        
        self.listWidget_devices.clear()
        self.pushButton_scan.setEnabled(False)
        adapter.scan_for(10000)
        self.pushButton_scan.setEnabled(True)

        peripheral_list = adapter.scan_get_results()
        for peripheral in peripheral_list:
            if "NINA" in peripheral.identifier():
                self.target_peripheral[peripheral.identifier()] = peripheral
                self.listWidget_devices.addItem(f"{peripheral.identifier()}")

    def connect(self):

        if self.target_peripheral.items():

            peripheral = self.target_peripheral[self.listWidget_devices.currentItem().text()]
            
            peripheral.connect()
            
            peripheral.notify(UUID_SPS, UUID_FIFO, lambda data: self.read(data))
            
            self.pushButton_scan.setEnabled(False)
            
            self.pushButton_write.setEnabled(True)
            self.pushButton_write.clicked.connect(lambda : self.write(peripheral))
            
            self.pushButton_disconnect.setEnabled(True)
            self.pushButton_disconnect.clicked.connect(lambda : self.disconnect(peripheral))
            
            self.pushButton_connect.setEnabled(False)

            self.textEdit_connected.setPlainText(peripheral.identifier())

    def write(self, peripheral):
        peripheral.write_request(UUID_SPS, UUID_FIFO, self.lineEdit.text().encode('ascii'))
        self.lineEdit.setText("")

    def read(self, data):
        self.listWidget_rcv_data.addItem(f"{datetime.now().isoformat()} - {data.decode('ascii')}")

    def disconnect(self, peripheral):
        peripheral.disconnect()
        self.pushButton_disconnect.setEnabled(False)
        self.pushButton_connect.setEnabled(True)
        self.pushButton_scan.setEnabled(True)
        self.textEdit_connected.setPlainText("")
        self.target_peripheral = {}

    def exit(self):
        sys.exit()

    def clear(self):
        self.listWidget_rcv_data.clear()

if __name__ == "__main__":
    app = QApplication([])
    win = Window()
    win.show()
    sys.exit(app.exec())
