import psutil
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
oke = False
ok_serv = False
flag = 1
flag_low = 0

unlockCar = '0xfd02'
conexiune = None



class Ui_MainWindow(object):
    pub_key = 0
    pri_key = 0
    conex = 0

    def setupUi(self, MainWindow):
        global server

        global server_created_flag
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(600, 500)
        MainWindow.setWindowTitle('Server')
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)

        self.centralwidget.setStyleSheet("background-color:white;")

        # Start server button
        self.server_start = QtWidgets.QPushButton(MainWindow)
        self.server_start.setText("Start server")
        self.server_start.setStyleSheet("font: bold; font-size: 15px;")
        self.server_start.setGeometry(QtCore.QRect(200, 170, 200, 41))
        self.server_start.clicked.connect(self.start_server)

        # Start server label
        self.server_label = QtWidgets.QLabel(self.centralwidget)
        self.server_label.setGeometry(QtCore.QRect(200, 210, 200, 40))
        self.server_label.setStyleSheet("font:bold;font-size: 15px;qproperty-alignment: AlignCenter;")

        # Key button
        self.key = QtWidgets.QPushButton(self.centralwidget)
        self.key.setGeometry(QtCore.QRect(225, 270, 150, 150))
        keyImage = QtGui.QIcon('./key.png')
        self.key.setIcon(keyImage)
        self.key.setIconSize(QtCore.QSize(80, 80))
        self.key.clicked.connect(self.send_key_data)
        self.key.setEnabled(False)

        # Unlock
        self.unlock = QtWidgets.QLabel(self.centralwidget)
        self.unlock.setGeometry(QtCore.QRect(225, 430, 150, 20))
        self.unlock.setText("Unlock the car!")
        self.unlock.setStyleSheet("font:bold;font-size: 15px;qproperty-alignment: AlignCenter;")

        # Dashboard image
        self.dashboard_label = QtWidgets.QLabel(self.centralwidget)
        self.dashboard_label.setGeometry(QtCore.QRect(120, 280, 360, 180))
        dashboard = QtGui.QImage(QtGui.QImageReader('./dashboard.png').read())
        self.dashboard_label.setPixmap(QtGui.QPixmap(dashboard))
        self.dashboard_label.setVisible(False)

        # Airgab image label
        self.airbag_label = QtWidgets.QLabel(self.centralwidget)
        self.airbag_label.setGeometry(QtCore.QRect(290, 365, 30, 30))
        airbag_image = QtGui.QPixmap("./airbag.png")
        airbag_image = airbag_image.scaled(30, 30, QtCore.Qt.KeepAspectRatio)
        self.airbag_label.setPixmap(QtGui.QPixmap(airbag_image))
        self.airbag_label.setVisible(False)

        # Ecu defect label
        self.ecu_defect_label = QtWidgets.QLabel(self.centralwidget)
        self.ecu_defect_label.setGeometry(QtCore.QRect(280, 365, 40, 30))
        self.ecu_defect_label.setStyleSheet("font:bold;font-size:12px;color:red")
        self.ecu_defect_label.setVisible(False)

        # Continental image
        self.conti_label = QtWidgets.QLabel(self.centralwidget)
        self.conti_label.setGeometry(QtCore.QRect(110, 30, 400, 100))
        continental = QtGui.QImage(QtGui.QImageReader('./rsz_conti.png').read())
        self.conti_label.setPixmap(QtGui.QPixmap(continental))

        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.show()


    def start_server(self):
        global server
        global PORT
        global HOST


        uplu = rsa_library.generate_keypair(277, 239)
        public_key = uplu[0][0]  # e
        modulus = uplu[0][1]  # n
        private_key = uplu[1][0]  # d


        self.pub_key = (public_key, modulus)
        self.pri_key = (private_key, modulus)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST, PORT))
        s.listen(3)
        global conexiune
        conexiune, addr = s.accept()
        self.key.setEnabled(True)
        self.airbag_label.setVisible(False)
        self.ecu_defect_label.clear()
        self.dashboard_label.setVisible(False)
        self.key.setVisible(True)
        self.unlock.setVisible(True)
        self.images()
        print("Connected")
        self.server_label.setText("Client connected")
        self.conex = conexiune
        conexiune.send((str(public_key) + "/" + str(private_key) + "/" + str(modulus)).encode())
        ok_serv = True
        self.thread = threading.Thread(target= self.recv_messages_handler, args=(1,))
        self.thread.start()


    def send_key_data(self):
        global conexiune
        conexiune.send(hex(rsa_library.encrypt(self.pub_key, int(unlockCar, 16))).encode())


    def recv_messages(self):
        receive_messages_thread = threading.Thread(target=self.recv_messages_handler, daemon=True, args=(1,))
        receive_messages_thread.start()

    def recv_messages_handler(self, stop_event):
        global conexiune
        global flag
        global flag_low

        while True:
            try:
                data = self.conex.recv(1024)
            except socket.error as e:
                print(str(e))
                break
            if not data:
                break
            data = rsa_library.decrypt(self.pri_key, int(data.decode(), 16))
            print(hex(data))
            flag_low = rsa_library.low_check(data)
            flag = rsa_library.number_check(data)

            if flag_low and flag:
                conexiune.send(hex(rsa_library.encrypt(self.pub_key, 0x0000)).encode())
            elif not flag_low and not flag:
                conexiune.send(hex(rsa_library.encrypt(self.pub_key, 0x1000)).encode())
            elif not flag_low:
                conexiune.send(hex(rsa_library.encrypt(self.pub_key, 0x2000)).encode())
            elif not flag:
                conexiune.send(hex(rsa_library.encrypt(self.pub_key, 0x3000)).encode())

        conexiune.close()



    def images(self):
        self.c_thread1 = threading.Thread(name='images', target=self.images_handler)
        self.c_thread1.start()

    def images_handler(self):
        global flag
        global flag_low
        global oke
        while True:
            if flag_low == True and flag == True:
                self.ecu_defect_label.setVisible(False)
                self.airbag_label.setVisible(True)
            elif (flag_low == True and flag == False):
                self.airbag_label.setVisible(False)
                self.ecu_defect_label.setVisible(True)
                self.ecu_defect_label.setText('  ECU\nDefect')
            elif flag_low == False and flag == False:
                self.airbag_label.setVisible(False)
                self.ecu_defect_label.setVisible(True)
                self.ecu_defect_label.setText('  ECU\nDefect')


class MyWindow(QtWidgets.QMainWindow):
    def closeEvent(self, event):
        result = QtWidgets.QMessageBox.question(self,
                                                "Confirm Exit",
                                                "Are you sure you want to exit ?",
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

        if result == QtWidgets.QMessageBox.Yes:
            event.accept()
        elif result == QtWidgets.QMessageBox.No:
            event.ignore()

    def center(self):
        frameGm = self.frameGeometry()
        screen = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
        centerPoint = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())


def kill_proc_tree(pid, including_parent=True):
    parent = psutil.Process(pid)
    if including_parent:
        parent.kill()


def main():
    global server_created_flag
    import sys
    global app
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = MyWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.center()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

me = os.getpid()
kill_proc_tree(me)
