# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'nicopealert.ui'
#
# Created: Mon Jun 01 20:39:35 2009
#      by: PyQt4 UI code generator 4.4.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_MainWindow(object):
  def setupUi(self, MainWindow):
    MainWindow.setObjectName("MainWindow")
    MainWindow.resize(708, 458)
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap(":/dic.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    MainWindow.setWindowIcon(icon)
    self.centralwidget = QtGui.QWidget(MainWindow)
    self.centralwidget.setObjectName("centralwidget")
    self.gridLayout = QtGui.QGridLayout(self.centralwidget)
    self.gridLayout.setObjectName("gridLayout")
    MainWindow.setCentralWidget(self.centralwidget)
    self.menubar = QtGui.QMenuBar(MainWindow)
    self.menubar.setGeometry(QtCore.QRect(0, 0, 708, 18))
    self.menubar.setObjectName("menubar")
    MainWindow.setMenuBar(self.menubar)
    self.statusbar = QtGui.QStatusBar(MainWindow)
    self.statusbar.setObjectName("statusbar")
    MainWindow.setStatusBar(self.statusbar)

    self.retranslateUi(MainWindow)
    QtCore.QMetaObject.connectSlotsByName(MainWindow)

  def retranslateUi(self, MainWindow):
    MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "ニコペアラート", None, QtGui.QApplication.UnicodeUTF8))

import nicopealert_rc

if __name__ == "__main__":
  import sys
  app = QtGui.QApplication(sys.argv)
  MainWindow = QtGui.QMainWindow()
  ui = Ui_MainWindow()
  ui.setupUi(MainWindow)
  MainWindow.show()
  sys.exit(app.exec_())

