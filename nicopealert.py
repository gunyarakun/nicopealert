#!/usr/local/bin/python
# -*- coding: utf-8 -*-

# ニコニコ大百科用アラートツール
# by Tasuku SUENAGA (a.k.a. gunyarakun)

# TODO: ニコ生、行の追加・更新・削除にロックが必要。
# TODO: 検索条件付与
# TODO: コミュアイコン取得
# TODO: 生ごとの詳細表示

from PyQt4 import QtCore, QtGui
from ui_mainwindow import Ui_MainWindow
from nicopoll import NicoPoll

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
  POLLING_DURATION = 10000 # 20000msec = 20sec

  COL_NAMES = [u'ID', u'タイトル', u'コミュ名', u'生主', u'来場数', u'コメ数', u'カテゴリ', u'説明文']
  COL_KEYS = [u'live_id', u'title', u'com_name', u'user_name', u'watcher_count', u'comment_count', u'category', u'desc']
  COL_WATCHER_INDEX = 4
  COL_COMMENT_INDEX = 5

  def __init__(self, mainWindow):
    QtGui.QStandardItemModel.__init__(self, 0, len(self.COL_NAMES), mainWindow)
    self.mainWindow = mainWindow;

    # set header
    for i, c in enumerate(self.COL_NAMES):
      self.setHeaderData(i, QtCore.Qt.Horizontal, QtCore.QVariant(c))

    # first data fetch
    self.nicopoll = NicoPoll(self.event_callback)
    self.nicopoll.fetch()

    # set timer for polling
    self.timer = QtCore.QTimer(self)
    self.connect(self.timer, QtCore.SIGNAL('timeout()'), self.timer_handler)
    self.timer.setInterval(self.POLLING_DURATION)
    self.timer.start()

  def timer_handler(self):
    self.nicopoll.fetch()

  def event_callback(self, type, event):
    if type == 'current_lives':
      self.current_lives(event)
    elif type == 'live':
      self.live_handler(event)
    elif type == 'dic':
      self.dic_handler(event)
    else:
      print '**** ababa ****'

  def dic_handler(self, event):
    pass

  def current_lives(self, lives):
    # 現在の生放送一覧から、
    # 1. 終わってしまった生放送を取り除く
    # 2. 放送中の生放送の視聴者数とコメント数を更新する

    rows = self.rowCount()

    for row in xrange(0, rows):
      live_id = unicode(self.item(row, 0).text())

      if lives.has_key(live_id):
        print 'live %s count to be freshed' % live_id
        item = QtGui.QStandardItem()
        item.setData(QtCore.QVariant(lives[live_id]['watcher_count']),
                     QtCore.Qt.DisplayRole)
        self.setItem(row, self.COL_WATCHER_INDEX, item)

        item = QtGui.QStandardItem()
        item.setData(QtCore.QVariant(lives[live_id]['comment_count']),
                     QtCore.Qt.DisplayRole)
        self.setItem(row, self.COL_COMMENT_INDEX, item)
      else:
        print 'live %s is deleted...' % (live_id)
        self.removeRow(row)

  def live_handler(self, event):
    live_id = event['live_id']
    print 'live %s to be added...' % live_id

    row = self.rowCount()
    self.setRowCount(row + 1)

    live_detail = self.nicopoll.live_details[live_id]

    for i, key in enumerate(self.COL_KEYS):
      item = QtGui.QStandardItem()
      val = live_detail[key]
      if isinstance(val, basestring):
        str = self.RE_LF.sub('', live_detail[key])
        item.setData(QtCore.QVariant(QtCore.QString(str)),
                     QtCore.Qt.DisplayRole)
      elif isinstance(val, int):
        item.setData(QtCore.QVariant(val),
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

    self.trayIconImg = QtGui.QIcon(self.tr('dic.ico'))
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
