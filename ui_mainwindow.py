# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'nicopealert.ui'
#
# Created: Wed May 27 09:36:53 2009
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
    self.menu = QtGui.QMenu(self.menubar)
    self.menu.setObjectName("menu")
    MainWindow.setMenuBar(self.menubar)
    self.statusbar = QtGui.QStatusBar(MainWindow)
    self.statusbar.setObjectName("statusbar")
    MainWindow.setStatusBar(self.statusbar)
    self.menubar.addAction(self.menu.menuAction())

    self.retranslateUi(MainWindow)
    QtCore.QMetaObject.connectSlotsByName(MainWindow)

  def retranslateUi(self, MainWindow):
    MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "ニコ百アラート", None, QtGui.QApplication.UnicodeUTF8))
    self.menu.setTitle(QtGui.QApplication.translate("MainWindow", "ファイル", None, QtGui.QApplication.UnicodeUTF8))

import nicopealert_rc

if __name__ == "__main__":
  import sys
  app = QtGui.QApplication(sys.argv)
  MainWindow = QtGui.QMainWindow()
  ui = Ui_MainWindow()
  ui.setupUi(MainWindow)
  MainWindow.show()
  sys.exit(app.exec_())

