#!/usr/bin/local/python
# -*- coding: utf-8 -*-

# ニコニコ大百科用アラートツール
# by Tasuku SUENAGA (a.k.a gunyarakun)

# TODO: 開始時間・来場者数・コメ数・コミュ限定・タグ・顔出し・アラート対象
# TODO: 検索条件付与
# TODO: コミュアイコン取得
# TODO: 生ごとの詳細表示
# TODO: nicoliveタイマー取得
# TODO: nicoliveいらないもの処理GC

from PyQt4 import QtCore, QtGui
from ui_mainwindow import Ui_MainWindow
from nicolive import NicoLive

import webbrowser

class NicoLiveTreeNode:
   def __init__(self, data, parent = None):
     self.data = data
     self.parent = parent
     self.children = []

   def addChild(self, data):
     node = NicoLiveTreeNode(data, self)
     self.children.append(node)
     return node

   def row(self):
     if self.parent:
       return self.parent.children.index(self)
     else:
       return 0

class NicoLiveTreeViewModel(QtGui.QStandardItemModel):
  import re

  RE_LF = re.compile(r'\r?\n')

  COL_NAMES = [u'ID', u'タイトル', u'コミュ名', u'生主', u'説明文']
  COL_KEYS = ['live_id_str', 'title', 'com_text', 'nusi', 'desc']

  def __init__(self, mainWindow):
    QtGui.QStandardItemModel.__init__(self, 0, len(self.COL_NAMES), mainWindow)
    self.mainWindow = mainWindow;

    # set header
    for i, c in enumerate(self.COL_NAMES):
      self.setHeaderData(i, QtCore.Qt.Horizontal, QtCore.QVariant(c))
    self.nicolive = NicoLive(self.append)
    self.nicolive.fetch()

  def append(self, live_id):
    row = self.rowCount()
    self.setRowCount(row + 1)

    live_detail = self.nicolive.live_details[live_id]

    for i, key in enumerate(self.COL_KEYS):
      item = QtGui.QStandardItem()
      str = self.RE_LF.sub('', live_detail[key])
      # FIXME: str() for nicolive id
      item.setData(QtCore.QVariant(QtCore.QString(str)),
                   QtCore.Qt.DisplayRole)
      item.setEditable(False)
      self.setItem(row, i, item)

      self.mainWindow.trayIcon.showMessage(QtCore.QString(u'新着生放送'),
                                           QtCore.QString(live_detail['title']))

class MainWindow(QtGui.QMainWindow):
  def __init__(self, app):
    QtGui.QDialog.__init__(self)
    self.app = app

    self.ui = Ui_MainWindow()
    self.ui.setupUi(self)

    # liveTreeView

    self.liveTreeView = self.ui.liveTreeView
    self.liveTreeViewModel = NicoLiveTreeViewModel(self)
    self.liveTreeView.setModel(self.liveTreeViewModel)
    self.liveTreeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
    self.liveTreeView.setColumnWidth(0, 80)
    self.liveTreeView.setSortingEnabled(True)

    self.connect(self.liveTreeView,
                 QtCore.SIGNAL('customContextMenuRequested(const QPoint &)'),
                 self.liveTreeContextMenu)

    # trayIcon/trayIconMenu/trayIconImg

    self.trayIconImg = QtGui.QIcon(self.tr('dic.gif'))
    self.trayIconMenu = QtGui.QMenu(self)
    # self.trayIconMenu.addAction(u'終了')
    self.trayIcon = QtGui.QSystemTrayIcon(self)
    self.trayIcon.setContextMenu(self.trayIconMenu)
    self.trayIcon.setIcon(self.trayIconImg)
    self.trayIcon.show()

    # buttons

    self.connect(self.ui.pushButton, QtCore.SIGNAL('clicked()'),
                 self.accept)

  def accept(self):
    pass

  def liveTreeContextMenu(self, point):
    tree_index = self.liveTreeView.indexAt(point)
    target_live_id = self.liveTreeViewModel.item(tree_index.row(), 0).text()
    url = 'http://live.nicovideo.jp/watch/' + target_live_id

    popup_menu = QtGui.QMenu(self)
    popup_menu.addAction(u'生放送を見る', lambda: webbrowser.open(url))
    popup_menu.addAction(u'URLをコピー', lambda: self.app.clipboard().setText(QtCore.QString(url)))
    #popup_menu.addSeparator()
    #popup_menu.addAction(u'コミュニティを通知対象にする')
    #popup_menu.addAction(u'主を通知対象にする')
    popup_menu.exec_(self.liveTreeView.mapToGlobal(point))

if __name__ == '__main__':
  import sys
  import codecs # for debug

  app = QtGui.QApplication(sys.argv)
  mw = MainWindow(app)
  mw.show()
  sys.exit(app.exec_())
