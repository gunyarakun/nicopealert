#!/usr/local/bin/python
# -*- coding: utf-8 -*-

# ニコニコ大百科用アラートツール
# by Tasuku SUENAGA (a.k.a. gunyarakun)

# TODO: treeViewいらない！listでいい！
# TODO: 検索条件付与
# TODO: コミュアイコン取得
# TODO: 生ごとの詳細表示

from PyQt4 import QtCore, QtGui
from ui_mainwindow import Ui_MainWindow
from nicopoll import NicoPoll
from datetime import datetime
import threading
import webbrowser
import re

class NicoDicTreeViewModel(QtGui.QStandardItemModel):
  COL_NAMES = [u'記事種別', u'記事名', u'コメント', u'時刻']
  COL_KEYS = [u'category', u'view_title', u'comment', u'time']

  RE_LF = re.compile(r'\r?\n')

  def __init__(self, mainWindow):
    QtGui.QStandardItemModel.__init__(self, 0, len(self.COL_NAMES), mainWindow)
    self.mainWindow = mainWindow;
    for i, c in enumerate(self.COL_NAMES):
      self.setHeaderData(i, QtCore.Qt.Horizontal, QtCore.QVariant(c))

  def append_event(self, events):
    for e in events:
      row = self.rowCount()
      self.setRowCount(row + 1)

      # TODO: 現在設定されているソート順を考慮した挿入
      for i, key in enumerate(self.COL_KEYS):
        item = QtGui.QStandardItem()
        val = e[key]
        if isinstance(val, basestring):
          str = self.RE_LF.sub('', val)
          item.setData(QtCore.QVariant(QtCore.QString(str)),
                       QtCore.Qt.DisplayRole)
        elif isinstance(val, int) or isinstance(val, datetime):
          item.setData(QtCore.QVariant(val),
                       QtCore.Qt.DisplayRole)
          
        item.setEditable(False)
        self.setItem(row, i, item)

class NicoLiveTreeViewModel(QtGui.QStandardItemModel):

  RE_LF = re.compile(r'\r?\n')

  COL_NAMES = [u'ID', u'タイトル', u'コミュ名', u'生主', u'来場数', u'コメ数', u'カテゴリ', u'開始時刻']
  COL_KEYS = [u'live_id', u'title', u'com_name', u'user_name', u'watcher_count', u'comment_count', u'category', u'time']
  COL_WATCHER_INDEX = 4
  COL_COMMENT_INDEX = 5

  lock = threading.Lock()

  def __init__(self, mainWindow):
    QtGui.QStandardItemModel.__init__(self, 0, len(self.COL_NAMES), mainWindow)
    self.mainWindow = mainWindow;
    for i, c in enumerate(self.COL_NAMES):
      self.setHeaderData(i, QtCore.Qt.Horizontal, QtCore.QVariant(c))

  def current_lives(self, lives):
    # 現在の生放送一覧から、
    # 1. 終わってしまった生放送を取り除く
    # 2. 放送中の生放送の視聴者数とコメント数を更新する

    rows = self.rowCount()

    try:
      self.lock.acquire()
      for row in xrange(0, rows):
        live_id = unicode(self.item(row, 0).text())

        if lives.has_key(live_id):
          # print 'live %s count to be freshed' % live_id
          item = QtGui.QStandardItem()
          item.setData(QtCore.QVariant(lives[live_id]['watcher_count']),
                       QtCore.Qt.DisplayRole)
          item.setEditable(False)
          self.setItem(row, self.COL_WATCHER_INDEX, item)

          item = QtGui.QStandardItem()
          item.setData(QtCore.QVariant(lives[live_id]['comment_count']),
                       QtCore.Qt.DisplayRole)
          item.setEditable(False)
          self.setItem(row, self.COL_COMMENT_INDEX, item)
        else:
          # print 'live %s is deleted...' % (live_id)
          self.removeRow(row)
      # TODO: 現在設定されているソート順で並べなおす
    finally:
      self.lock.release()

  def live_handler(self, detail):
    # print 'live %s to be added...' % detail[u'live_id']

    try:
      self.lock.acquire()
      row = self.rowCount()
      self.setRowCount(row + 1)

      # TODO: 現在設定されているソート順を考慮した挿入
      for i, key in enumerate(self.COL_KEYS):
        item = QtGui.QStandardItem()
        val = detail[key]
        if isinstance(val, basestring):
          str = self.RE_LF.sub('', detail[key])
          item.setData(QtCore.QVariant(QtCore.QString(str)),
                       QtCore.Qt.DisplayRole)
        elif isinstance(val, int) or isinstance(val, datetime):
          item.setData(QtCore.QVariant(val),
                       QtCore.Qt.DisplayRole)
          
        item.setEditable(False)
        self.setItem(row, i, item)

        self.mainWindow.trayIcon.showMessage(QtCore.QString(u'新着生放送'),
                                             QtCore.QString(detail['title']))
    finally:
      self.lock.release()

class MainWindow(QtGui.QMainWindow):
  POLLING_DURATION = 10000 # 20000msec = 20sec

  def __init__(self, app):
    QtGui.QDialog.__init__(self)
    self.app = app

    self.ui = Ui_MainWindow()
    self.ui.setupUi(self)

    # dicTreeView
    self.dicTreeView = self.ui.dicTreeView
    self.dicTreeViewModel = NicoDicTreeViewModel(self)
    self.dicTreeView.setModel(self.dicTreeViewModel)
    self.dicTreeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
    self.dicTreeView.setColumnWidth(0, 80)
    self.dicTreeView.setSortingEnabled(True)

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

    self.connect(self.ui.dicFilterPushButton, QtCore.SIGNAL('clicked()'),
                 self.showDicFilter)
    self.connect(self.ui.liveFilterPushButton, QtCore.SIGNAL('clicked()'),
                 self.showLiveFilter)

    # first data fetch
    self.nicopoll = NicoPoll(self.dicTreeViewModel,
                             self.liveTreeViewModel)
    self.nicopoll.fetch()

    # set timer for polling
    self.timer = QtCore.QTimer(self)
    self.connect(self.timer, QtCore.SIGNAL('timeout()'), self.timer_handler)
    self.timer.setInterval(self.POLLING_DURATION)
    self.timer.start()

  def timer_handler(self):
    self.nicopoll.fetch()

  def showDicFilter(self):
    pass

  def showLiveFilter(self):
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
