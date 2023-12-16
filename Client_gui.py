import psutil as psutil
from PyQt5 import QtCore, QtGui, QtWidgets, QtTest
import socket

from PyQt5.QtCore import QThread, pyqtSignal

import rsa_library
import _pickle as cPickle
import os
import threading
import sys, time

HOST = 'localhost'
PORT = 12346
ok_client = False
airbag_on = '0xfe01'
corrupted_low = '0xfe32'
corrupted_high = '0x5701'


class Ui_MainWindow(object):
    se = 0
    priv_k = 0
    pub_k = 0
    modul = 0
    ok1 = False

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(600, 500)
        MainWindow.setWindowTitle('Client')
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        MainWindow.setCentralWidget(self.centralwidget)

        self.centralwidget.setStyleSheet("background-color:white;")

        # Start client button
        self.client_start = QtWidgets.QPushButton(MainWindow)
        self.client_start.setText("Connect client")
        self.client_start.setStyleSheet("font: bold; font-size: 15px;")
        self.client_start.setGeometry(QtCore.QRect(200, 170, 200, 40))
        self.client_start.clicked.connect(self.start_client)

        self.client_label = QtWidgets.QLabel(self.centralwidget)
        self.client_label.setGeometry(QtCore.QRect(320, 170, 205, 41))
        self.client_label.setStyleSheet("font:bold;font-size: 15px;")

        # Connected label
        self.connected_label = QtWidgets.QLabel(self.centralwidget)
        self.connected_label.setGeometry(QtCore.QRect(200, 210, 200, 40))
        self.connected_label.setStyleSheet("font-size:15px;font:bold;qproperty-alignment: AlignCenter;")

        # Airbag on
        self.airbag = QtWidgets.QPushButton(MainWindow)
        self.airbag.setText("Airbag on")
        self.airbag.setStyleSheet("font: bold; font-size: 15px;")
        self.airbag.setGeometry(QtCore.QRect(70, 260, 211, 41))
        self.airbag.clicked.connect(self.send_on_data)
        self.airbag.setEnabled(False)

        # Airbag on label
        self.airbag_on_label = QtWidgets.QLabel(self.centralwidget)
        self.airbag_on_label.setGeometry(QtCore.QRect(300, 260, 200, 40))
        self.airbag_on_label.setStyleSheet("font-size:15px;font:bold;qproperty-alignment: AlignCenter;")

        # Corrupted low
        self.corrupted_low = QtWidgets.QPushButton(MainWindow)
        self.corrupted_low.setText("Corrupted low")
        self.corrupted_low.setStyleSheet("font: bold; font-size: 15px;")
        self.corrupted_low.setGeometry(QtCore.QRect(70, 330, 211, 41))
        self.corrupted_low.clicked.connect(self.send_corrupted_low)
        self.corrupted_low.setEnabled(False)

        # Corrupted low label
        self.corrupted_low_label = QtWidgets.QLabel(self.centralwidget)
        self.corrupted_low_label.setGeometry(QtCore.QRect(300, 330, 200, 40))
        self.corrupted_low_label.setStyleSheet("font-size:15px;font:bold;qproperty-alignment: AlignCenter;")

        # Corrupted high
        self.corrupted_high = QtWidgets.QPushButton(MainWindow)
        self.corrupted_high.setText("Corrupted high")
        self.corrupted_high.setStyleSheet("font: bold; font-size: 15px;")
        self.corrupted_high.setGeometry(QtCore.QRect(70, 400, 211, 41))
        self.corrupted_high.clicked.connect(self.send_corrupted_high)
        self.corrupted_high.setEnabled(False)

        # Corrupted high label
        self.corrupted_high_label = QtWidgets.QLabel(self.centralwidget)
        self.corrupted_high_label.setGeometry(QtCore.QRect(300, 400, 200, 40))
        self.corrupted_high_label.setStyleSheet("font-size:15px;font:bold;qproperty-alignment: AlignCenter;")

        # Continental image
        self.conti_label = QtWidgets.QLabel(self.centralwidget)
        self.conti_label.setGeometry(QtCore.QRect(110, 30, 400, 100))
        continental = QtGui.QImage(QtGui.QImageReader('./rsz_conti.png').read())
        self.conti_label.setPixmap(QtGui.QPixmap(continental))

        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")

        MainWindow.setStatusBar(self.statusbar)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.show()


    def start_client(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((HOST, PORT))
        self.pub_k, self.priv_k, self.modul = self.s.recv(1024).decode().split("/")
        self.pub_k = int(self.pub_k)
        self.priv_k = int(self.priv_k)
        self.modul = int(self.modul)
        print("public key: " + str(self.pub_k))
        print("private key: " + str(self.priv_k))
        print("modul: " + str(self.modul))
        self.thread = threading.Thread(target=self.recv_handler, args=(1,))
        self.thread.start()


    def recv_messages(self):
        pass

    def recv_handler(self, stop_event):
        while True:
            try:
                data = self.s.recv(1024)
            except socket.error as e:
                print(str(e))
                break
            if not data:
                break


            data = rsa_library.decrypt((self.priv_k, self.modul), int(data.decode(), 16))
            print(hex(data))
            if data == 0x0000:
                self.airbag_on_label.setText("airbag on")
            elif data == 0x1000:
                self.corrupted_low_label.setText("corrupted low")
                self.corrupted_high_label.setText("corrupted high")
            elif data == 0x2000:
                self.corrupted_low_label.setText("corrupted low")
            elif data == 0x3000:
                self.corrupted_high_label.setText("corrupted high")
            elif data == 0xfd02:
                print("Unlocked car")
                self.corrupted_low.setEnabled(True)
                self.corrupted_high.setEnabled(True)
                self.airbag.setEnabled(True)
                self.airbag_on_label.setText("")
                self.corrupted_high_label.setText("")
                self.corrupted_low_label.setText("")



        self.s.close()
    def send_on_data(self):
        self.s.send(hex(rsa_library.encrypt((self.pub_k, self.modul), int(airbag_on, 16))).encode())



    def send_corrupted_low(self):
        self.s.send(hex(rsa_library.encrypt((self.pub_k, self.modul), int(corrupted_low, 16))).encode())


    def send_corrupted_high(self):
        self.s.send(hex(rsa_library.encrypt((self.pub_k, self.modul), int(corrupted_high, 16))).encode())

    def kill_proc_tree(self, pid, including_parent=True):
        parent = psutil.Process(pid)
        if including_parent:
            parent.kill()


class MyWindow(QtWidgets.QMainWindow):
    def closeEvent(self, event):
        result = QtGui.QMessageBox.question(self,
                                            "Confirm Exit",
                                            "Are you sure you want to exit ?",
                                            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)

        if result == QtGui.QMessageBox.Yes:
            event.accept()
        elif result == QtGui.QMessageBox.No:
            event.ignore()

    def center(self):
        frameGm = self.frameGeometry()
        screen = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
        centerPoint = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = MyWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.center()
    sys.exit(app.exec_())

me = os.getpid()
# kill_proc_tree(me)
