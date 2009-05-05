# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'nicopealert.ui'
#
# Created: Wed May 06 08:14:47 2009
#      by: PyQt4 UI code generator 4.4.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_MainWindow(object):
  def setupUi(self, MainWindow):
    MainWindow.setObjectName("MainWindow")
    MainWindow.resize(401, 468)
    self.centralwidget = QtGui.QWidget(MainWindow)
    self.centralwidget.setObjectName("centralwidget")
    self.gridLayout = QtGui.QGridLayout(self.centralwidget)
    self.gridLayout.setObjectName("gridLayout")
    self.tabWidget = QtGui.QTabWidget(self.centralwidget)
    self.tabWidget.setLayoutDirection(QtCore.Qt.LeftToRight)
    self.tabWidget.setObjectName("tabWidget")
    self.tab = QtGui.QWidget()
    sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(self.tab.sizePolicy().hasHeightForWidth())
    self.tab.setSizePolicy(sizePolicy)
    self.tab.setObjectName("tab")
    self.gridLayout_2 = QtGui.QGridLayout(self.tab)
    self.gridLayout_2.setObjectName("gridLayout_2")
    self.listView = QtGui.QListView(self.tab)
    self.listView.setObjectName("listView")
    self.gridLayout_2.addWidget(self.listView, 0, 0, 1, 1)
    self.horizontalLayout = QtGui.QHBoxLayout()
    self.horizontalLayout.setObjectName("horizontalLayout")
    spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
    self.horizontalLayout.addItem(spacerItem)
    self.pushButton = QtGui.QPushButton(self.tab)
    sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
    self.pushButton.setSizePolicy(sizePolicy)
    self.pushButton.setMinimumSize(QtCore.QSize(0, 16))
    self.pushButton.setLayoutDirection(QtCore.Qt.LeftToRight)
    self.pushButton.setObjectName("pushButton")
    self.horizontalLayout.addWidget(self.pushButton)
    self.gridLayout_2.addLayout(self.horizontalLayout, 5, 0, 1, 1)
    self.tabWidget.addTab(self.tab, "")
    self.tab_2 = QtGui.QWidget()
    self.tab_2.setObjectName("tab_2")
    self.tabWidget.addTab(self.tab_2, "")
    self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)
    MainWindow.setCentralWidget(self.centralwidget)
    self.menubar = QtGui.QMenuBar(MainWindow)
    self.menubar.setGeometry(QtCore.QRect(0, 0, 401, 19))
    self.menubar.setObjectName("menubar")
    self.menu = QtGui.QMenu(self.menubar)
    self.menu.setObjectName("menu")
    MainWindow.setMenuBar(self.menubar)
    self.statusbar = QtGui.QStatusBar(MainWindow)
    self.statusbar.setObjectName("statusbar")
    MainWindow.setStatusBar(self.statusbar)
    self.menubar.addAction(self.menu.menuAction())

    self.retranslateUi(MainWindow)
    self.tabWidget.setCurrentIndex(0)
    QtCore.QMetaObject.connectSlotsByName(MainWindow)

  def retranslateUi(self, MainWindow):
    MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "ニコ百アラート", None, QtGui.QApplication.UnicodeUTF8))
    self.pushButton.setText(QtGui.QApplication.translate("MainWindow", "PushButton", None, QtGui.QApplication.UnicodeUTF8))
    self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QtGui.QApplication.translate("MainWindow", "大百科", None, QtGui.QApplication.UnicodeUTF8))
    self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QtGui.QApplication.translate("MainWindow", "Tab 2", None, QtGui.QApplication.UnicodeUTF8))
    self.menu.setTitle(QtGui.QApplication.translate("MainWindow", "ファイル", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
  import sys
  app = QtGui.QApplication(sys.argv)
  MainWindow = QtGui.QMainWindow()
  ui = Ui_MainWindow()
  ui.setupUi(MainWindow)
  MainWindow.show()
  sys.exit(app.exec_())

