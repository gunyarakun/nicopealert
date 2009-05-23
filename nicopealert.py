#!/usr/local/bin/python
# -*- coding: utf-8 -*-

# ニコニコ大百科用アラートツール
# by Tasuku SUENAGA (a.k.a. gunyarakun)

# TODO: sort/filter
# TODO: コミュ・ウォッチリスト登録
# TODO: 上記登録のもののみ通知 & 自動立ち上げ？
# TODO: カラム移動
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
import cPickle as pickle

class NicoDicTableModel(QtCore.QAbstractTableModel):
  COL_NAMES = [QtCore.QVariant(u'記事種別'),
               QtCore.QVariant(u'記事名'),
               QtCore.QVariant(u'コメント'),
               QtCore.QVariant(u'時刻')]
  COL_KEYS = [u'category', u'view_title', u'comment', u'time']

  RE_LF = re.compile(r'\r?\n')

  def __init__(self, mainWindow):
    QtCore.QAbstractTableModel.__init__(self, mainWindow)
    self.mainWindow = mainWindow
    self.datas = []

  def rowCount(self, parent):
    return len(self.datas)

  def columnCount(self, parent):
    return len(self.COL_NAMES)

  def data(self, index, role):
    if not index.isValid():
      return QtCore.QVariant()
    elif role != QtCore.Qt.DisplayRole:
      return QtCore.QVariant()
    return QtCore.QVariant(self.datas[index.row()][index.column()])

  def headerData(self, col, orientation, role):
    if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
      return self.COL_NAMES[col]
    return QtCore.QVariant()

  def append_event(self, events):
    if len(events) == 0:
      return
    rowcount = len(self.datas)
    self.beginInsertRows(QtCore.QModelIndex(), rowcount, rowcount + len(events) - 1)
    try:
      for e in events:
        row = []
        for key in self.COL_KEYS:
          item = QtGui.QStandardItem()
          val = e[key]
          if isinstance(val, basestring):
            str = self.RE_LF.sub('', val)
            row.append(QtCore.QVariant(QtCore.QString(str)))
          elif isinstance(val, int) or isinstance(val, datetime):
            row.append(QtCore.QVariant(val))
          elif val is None:
            row.append(QtCore.QVariant())
        self.datas.append(row)
    finally:
      self.endInsertRows()

class NicoLiveTableModel(QtCore.QAbstractTableModel):
  COL_NAMES = [QtCore.QVariant(u'ID'),
               QtCore.QVariant(u'タイトル'),
               QtCore.QVariant(u'コミュ名'),
               QtCore.QVariant(u'生主'),
               QtCore.QVariant(u'来場数'),
               QtCore.QVariant(u'コメ数'),
               QtCore.QVariant(u'カテゴリ'),
               QtCore.QVariant(u'開始時刻')]
  COL_KEYS = [u'live_id', u'title', u'com_name', u'user_name', u'watcher_count', u'comment_count', u'category', u'time']

  RE_LF = re.compile(r'\r?\n')

  COL_WATCHER_INDEX = 4
  COL_COMMENT_INDEX = 5

  lock = threading.Lock()

  def __init__(self, mainWindow):
    QtCore.QAbstractTableModel.__init__(self, mainWindow)
    self.mainWindow = mainWindow
    self.datas = []

  def rowCount(self, parent):
    return len(self.datas)

  def columnCount(self, parent):
    return len(self.COL_NAMES)

  def data(self, index, role):
    if not index.isValid():
      return QtCore.QVariant()
    elif role != QtCore.Qt.DisplayRole:
      return QtCore.QVariant()
    return QtCore.QVariant(self.datas[index.row()][index.column()])

  def headerData(self, col, orientation, role):
    if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
      return self.COL_NAMES[col]
    return QtCore.QVariant()

  def current_lives(self, lives):
    # 現在の生放送一覧から、
    # 1. 終わってしまった生放送を取り除く
    # 2. 放送中の生放送の視聴者数とコメント数を更新する

    self.lock.acquire()
    try:
      for row in xrange(0, self.datas):
        live_id = unicode(self.item(row, 0).text())

        if lives.has_key(live_id):
          # print 'live %s count to be freshed' % live_id
          self.datas[row][self.COL_WATCHER_INDEX] = QtCore.QVariant(
            lives[live_id]['watcher_count'])
          self.datas[row][self.COL_COMMENT_INDEX] = QtCore.QVariant(
            lives[live_id]['comment_count'])
        else:
          # print 'live %s is deleted...' % (live_id)
          # TODO: remove after!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
          # self.removeRow(row)
          pass
      st_index = self.index(0, self.COL_WATCHER_INDEX)
      ed_index = self.index(len(self.datas), self.COL_COMMENT_INDEX)
      self.dataChanged(st_index, ed_index)
    finally:
      self.lock.release()

  def live_handler(self, details):
    if len(details) == 0:
      return
    self.lock.acquire()
    try:
      rowcount = len(self.datas)
      self.beginInsertRows(QtCore.QModelIndex(), rowcount, rowcount + len(details) - 1)
      for d in details:
        row = []
        for key in self.COL_KEYS:
          val = d[key]
          if isinstance(val, basestring):
            str = self.RE_LF.sub('', val)
            row.append(QtCore.QVariant(QtCore.QString(str)))
          elif isinstance(val, int) or isinstance(val, datetime):
            row.append(QtCore.QVariant(val))
          elif val is None:
            row.append(QtCore.QVariant())
        self.datas.append(row)
      #self.mainWindow.trayIcon.showMessage(QtCore.QString(u'新着生放送'),
      #                                     QtCore.QString(d['title']))
    finally:
      self.endInsertRows()
      self.lock.release()

class DicFilterProxyModel(QtGui.QSortFilterProxyModel):
  def __init__(self, mainWindow):
    QtGui.QSortFilterProxyModel.__init__(self, mainWindow)
    self.watchlist = mainWindow.watchlist

  def filterAcceptsRow(self, source_row, source_parent):
    cond = False
    for i in xrange(self.sourceModel().columnCount(None)):
      idx = self.sourceModel().index(source_row, i, source_parent)
      cond |= self.sourceModel().data(idx, QtCore.Qt.DisplayRole).toString().contains(self.filterRegExp())
    return cond

class LiveFilterProxyModel(QtGui.QSortFilterProxyModel):
  def __init__(self, mainWindow):
    QtGui.QSortFilterProxyModel.__init__(self, mainWindow)
    self.communities = mainWindow.communities

  def filterAcceptsRow(self, source_row, source_parent):
    cond = False
    for i in xrange(self.sourceModel().columnCount(None)):
      idx = self.sourceModel().index(source_row, i, source_parent)
      cond |= self.sourceModel().data(idx, QtCore.Qt.DisplayRole).toString().contains(self.filterRegExp())
    return cond

class MainWindow(QtGui.QMainWindow):
  POLLING_DURATION = 10000 # 10000msec = 10sec

  def __init__(self, app):
    QtGui.QDialog.__init__(self)
    self.app = app

    self.ui = Ui_MainWindow()
    self.ui.setupUi(self)

    # load settings
    try:
      f = file('nicopealert.dat', 'rb')
      settings = pickle.load(f)
      self.watchlist = settings['watchlist']
      self.communities = settings['communities']
    except:
      self.watchlist = []
      self.communities = []

    # dicTreeView
    self.dicTreeView = self.ui.dicTreeView
    self.dicTableModel = NicoDicTableModel(self)
    self.dicFilterModel = DicFilterProxyModel(self)
    self.dicFilterModel.setSourceModel(self.dicTableModel)
    self.dicTreeView.setModel(self.dicFilterModel)
    self.dicTreeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
    self.dicTreeView.setColumnWidth(0, 80)
    self.dicTreeView.setSortingEnabled(True)
    self.dicTreeView.setRootIsDecorated(False)
    self.dicTreeView.setAlternatingRowColors(True)

    # liveTreeView
    self.liveTreeView = self.ui.liveTreeView
    self.liveTableModel = NicoLiveTableModel(self)
    self.liveFilterModel = LiveFilterProxyModel(self)
    self.liveFilterModel.setSourceModel(self.liveTableModel)
    self.liveTreeView.setModel(self.liveFilterModel)
    self.liveTreeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
    self.liveTreeView.setColumnWidth(0, 80)
    self.liveTreeView.setSortingEnabled(True)
    self.liveTreeView.setRootIsDecorated(False)
    self.liveTreeView.setAlternatingRowColors(True)

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

    # events
    self.connect(self.ui.dicFilterPushButton, QtCore.SIGNAL('clicked()'),
                 self.showDicFilter)
    self.connect(self.ui.liveFilterPushButton, QtCore.SIGNAL('clicked()'),
                 self.showLiveFilter)
    self.connect(self.ui.dicKeywordLineEdit,
                 QtCore.SIGNAL('textChanged(const QString &)'),
                 self.dicKeywordLineEditChanged)
    self.connect(self.ui.liveKeywordLineEdit,
                 QtCore.SIGNAL('textChanged(const QString &)'),
                 self.liveKeywordLineEditChanged)

    # first data fetch
    self.nicopoll = NicoPoll(self.dicTableModel,
                             self.liveTableModel)
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

  def dicKeywordLineEditChanged(self):
    regex = QtCore.QRegExp(self.ui.dicKeywordLineEdit.text(),
                           QtCore.Qt.CaseInsensitive,
                           QtCore.QRegExp.RegExp2)
    self.dicFilterModel.setFilterRegExp(regex)

  def liveKeywordLineEditChanged(self):
    regex = QtCore.QRegExp(self.ui.liveKeywordLineEdit.text(),
                           QtCore.Qt.CaseInsensitive,
                           QtCore.QRegExp.RegExp2)
    self.liveFilterModel.setFilterRegExp(regex)

  def liveTreeContextMenu(self, point):
    tree_index = self.liveTreeView.indexAt(point)
    live_index = self.liveFilterModel.index(tree_index.row(), 0)
    target_live_id = self.liveFilterModel.data(live_index).toString()
    print u'%s' % target_live_id
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
