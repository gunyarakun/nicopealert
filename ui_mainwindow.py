# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'nicopealert.ui'
#
# Created: Sat May 23 10:32:04 2009
#      by: PyQt4 UI code generator 4.4.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_MainWindow(object):
  def setupUi(self, MainWindow):
    MainWindow.setObjectName("MainWindow")
    MainWindow.resize(708, 458)
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap("dic.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    MainWindow.setWindowIcon(icon)
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
    self.horizontalLayout = QtGui.QHBoxLayout()
    self.horizontalLayout.setObjectName("horizontalLayout")
    self.label = QtGui.QLabel(self.tab)
    self.label.setObjectName("label")
    self.horizontalLayout.addWidget(self.label)
    self.dicKeywordLineEdit = QtGui.QLineEdit(self.tab)
    self.dicKeywordLineEdit.setObjectName("dicKeywordLineEdit")
    self.horizontalLayout.addWidget(self.dicKeywordLineEdit)
    spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
    self.horizontalLayout.addItem(spacerItem)
    self.dicWatchListCheckBox = QtGui.QCheckBox(self.tab)
    self.dicWatchListCheckBox.setObjectName("dicWatchListCheckBox")
    self.horizontalLayout.addWidget(self.dicWatchListCheckBox)
    self.dicFilterPushButton = QtGui.QPushButton(self.tab)
    sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(self.dicFilterPushButton.sizePolicy().hasHeightForWidth())
    self.dicFilterPushButton.setSizePolicy(sizePolicy)
    self.dicFilterPushButton.setMinimumSize(QtCore.QSize(0, 16))
    self.dicFilterPushButton.setLayoutDirection(QtCore.Qt.LeftToRight)
    self.dicFilterPushButton.setObjectName("dicFilterPushButton")
    self.horizontalLayout.addWidget(self.dicFilterPushButton)
    self.gridLayout_2.addLayout(self.horizontalLayout, 5, 0, 1, 1)
    self.dicTreeView = QtGui.QTreeView(self.tab)
    self.dicTreeView.setObjectName("dicTreeView")
    self.gridLayout_2.addWidget(self.dicTreeView, 0, 0, 1, 1)
    self.tabWidget.addTab(self.tab, icon, "")
    self.tab_2 = QtGui.QWidget()
    self.tab_2.setObjectName("tab_2")
    self.gridLayout_3 = QtGui.QGridLayout(self.tab_2)
    self.gridLayout_3.setObjectName("gridLayout_3")
    self.horizontalLayout_2 = QtGui.QHBoxLayout()
    self.horizontalLayout_2.setObjectName("horizontalLayout_2")
    self.label_2 = QtGui.QLabel(self.tab_2)
    self.label_2.setObjectName("label_2")
    self.horizontalLayout_2.addWidget(self.label_2)
    self.liveKeywordLineEdit = QtGui.QLineEdit(self.tab_2)
    self.liveKeywordLineEdit.setObjectName("liveKeywordLineEdit")
    self.horizontalLayout_2.addWidget(self.liveKeywordLineEdit)
    spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
    self.horizontalLayout_2.addItem(spacerItem1)
    self.liveCommunityCheckBox = QtGui.QCheckBox(self.tab_2)
    self.liveCommunityCheckBox.setObjectName("liveCommunityCheckBox")
    self.horizontalLayout_2.addWidget(self.liveCommunityCheckBox)
    self.liveFilterPushButton = QtGui.QPushButton(self.tab_2)
    sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(self.liveFilterPushButton.sizePolicy().hasHeightForWidth())
    self.liveFilterPushButton.setSizePolicy(sizePolicy)
    self.liveFilterPushButton.setMinimumSize(QtCore.QSize(0, 16))
    self.liveFilterPushButton.setObjectName("liveFilterPushButton")
    self.horizontalLayout_2.addWidget(self.liveFilterPushButton)
    self.gridLayout_3.addLayout(self.horizontalLayout_2, 5, 0, 1, 1)
    self.liveTreeView = QtGui.QTreeView(self.tab_2)
    self.liveTreeView.setObjectName("liveTreeView")
    self.gridLayout_3.addWidget(self.liveTreeView, 0, 0, 1, 1)
    icon1 = QtGui.QIcon()
    icon1.addPixmap(QtGui.QPixmap("live.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    self.tabWidget.addTab(self.tab_2, icon1, "")
    self.tab_3 = QtGui.QWidget()
    self.tab_3.setObjectName("tab_3")
    self.gridLayout_4 = QtGui.QGridLayout(self.tab_3)
    self.gridLayout_4.setObjectName("gridLayout_4")
    self.horizontalLayout_3 = QtGui.QHBoxLayout()
    self.horizontalLayout_3.setObjectName("horizontalLayout_3")
    spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
    self.horizontalLayout_3.addItem(spacerItem2)
    self.addWatchListPushButton = QtGui.QPushButton(self.tab_3)
    sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(self.addWatchListPushButton.sizePolicy().hasHeightForWidth())
    self.addWatchListPushButton.setSizePolicy(sizePolicy)
    self.addWatchListPushButton.setMinimumSize(QtCore.QSize(0, 16))
    self.addWatchListPushButton.setObjectName("addWatchListPushButton")
    self.horizontalLayout_3.addWidget(self.addWatchListPushButton)
    self.gridLayout_4.addLayout(self.horizontalLayout_3, 5, 0, 1, 1)
    self.watchListTreeView = QtGui.QTreeView(self.tab_3)
    self.watchListTreeView.setObjectName("watchListTreeView")
    self.gridLayout_4.addWidget(self.watchListTreeView, 0, 0, 1, 1)
    self.tabWidget.addTab(self.tab_3, icon, "")
    self.tab_4 = QtGui.QWidget()
    self.tab_4.setObjectName("tab_4")
    self.gridLayout_5 = QtGui.QGridLayout(self.tab_4)
    self.gridLayout_5.setObjectName("gridLayout_5")
    self.horizontalLayout_4 = QtGui.QHBoxLayout()
    self.horizontalLayout_4.setObjectName("horizontalLayout_4")
    spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
    self.horizontalLayout_4.addItem(spacerItem3)
    self.addCommunityPushButton = QtGui.QPushButton(self.tab_4)
    sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(self.addCommunityPushButton.sizePolicy().hasHeightForWidth())
    self.addCommunityPushButton.setSizePolicy(sizePolicy)
    self.addCommunityPushButton.setMinimumSize(QtCore.QSize(0, 16))
    self.addCommunityPushButton.setObjectName("addCommunityPushButton")
    self.horizontalLayout_4.addWidget(self.addCommunityPushButton)
    self.gridLayout_5.addLayout(self.horizontalLayout_4, 5, 0, 1, 1)
    self.communityTreeView = QtGui.QTreeView(self.tab_4)
    self.communityTreeView.setObjectName("communityTreeView")
    self.gridLayout_5.addWidget(self.communityTreeView, 0, 0, 1, 1)
    self.tabWidget.addTab(self.tab_4, icon1, "")
    self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)
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
    self.tabWidget.setCurrentIndex(0)
    QtCore.QMetaObject.connectSlotsByName(MainWindow)

  def retranslateUi(self, MainWindow):
    MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "ニコ百アラート", None, QtGui.QApplication.UnicodeUTF8))
    self.label.setText(QtGui.QApplication.translate("MainWindow", "検索キーワード", None, QtGui.QApplication.UnicodeUTF8))
    self.dicWatchListCheckBox.setText(QtGui.QApplication.translate("MainWindow", "ウォッチリスト限定", None, QtGui.QApplication.UnicodeUTF8))
    self.dicFilterPushButton.setText(QtGui.QApplication.translate("MainWindow", "この条件を保存", None, QtGui.QApplication.UnicodeUTF8))
    self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QtGui.QApplication.translate("MainWindow", "大百科", None, QtGui.QApplication.UnicodeUTF8))
    self.tabWidget.setTabToolTip(self.tabWidget.indexOf(self.tab), QtGui.QApplication.translate("MainWindow", "ニコニコ大百科のイベント一覧です。", None, QtGui.QApplication.UnicodeUTF8))
    self.label_2.setText(QtGui.QApplication.translate("MainWindow", "検索キーワード", None, QtGui.QApplication.UnicodeUTF8))
    self.liveCommunityCheckBox.setText(QtGui.QApplication.translate("MainWindow", "対象コミュニティ限定", None, QtGui.QApplication.UnicodeUTF8))
    self.liveFilterPushButton.setText(QtGui.QApplication.translate("MainWindow", "この条件を保存", None, QtGui.QApplication.UnicodeUTF8))
    self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QtGui.QApplication.translate("MainWindow", "生放送", None, QtGui.QApplication.UnicodeUTF8))
    self.tabWidget.setTabToolTip(self.tabWidget.indexOf(self.tab_2), QtGui.QApplication.translate("MainWindow", "ニコニコ生放送の放送一覧です。", None, QtGui.QApplication.UnicodeUTF8))
    self.addWatchListPushButton.setText(QtGui.QApplication.translate("MainWindow", "ウォッチリストを追加する", None, QtGui.QApplication.UnicodeUTF8))
    self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), QtGui.QApplication.translate("MainWindow", "ウォッチリスト", None, QtGui.QApplication.UnicodeUTF8))
    self.addCommunityPushButton.setText(QtGui.QApplication.translate("MainWindow", "コミュニティを追加", None, QtGui.QApplication.UnicodeUTF8))
    self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), QtGui.QApplication.translate("MainWindow", "対象コミュニティ", None, QtGui.QApplication.UnicodeUTF8))
    self.menu.setTitle(QtGui.QApplication.translate("MainWindow", "ファイル", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
  import sys
  app = QtGui.QApplication(sys.argv)
  MainWindow = QtGui.QMainWindow()
  ui = Ui_MainWindow()
  ui.setupUi(MainWindow)
  MainWindow.show()
  sys.exit(app.exec_())

