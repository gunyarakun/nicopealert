#!/usr/bin/python
# -*- coding: utf-8 -*-

# ニコニコ大百科用アラートツール
# by Tasuku SUENAGA (a.k.a. gunyarakun)

# TODO: すべてのタブをUserTabにする。
# TODO: ウォッチリスト/コミュニティリストの要素削除
# TODO: 検索条件の保存
# TODO: カラムサイズ初期値設定
# TODO: カラム移動・サイズの記憶
# TODO: 4つのTableModelの共通化
# TODO: watchlistの表記
# TODO: コミュ・ウォッチリスト対象の背景色変更
# TODO: timer_handlerのスレッド化。詰まることがあるかもしれないので。
# TODO: なくなった生を削除する部分の復活。
# TODO: 生ごとの詳細表示
# TODO: リファクタリング
# TODO: ネットワーク無効実験
# TODO: エラーハンドリング丁寧に、エラー報告ツール(ログとか)

from PyQt4 import QtCore, QtGui
from ui_mainwindow import Ui_MainWindow
from nicopoll import NicoPoll
from datetime import datetime
import threading
import re
import cPickle as pickle

from usertab import *

class NicoDicTableModel(QtCore.QAbstractTableModel):
  COL_NAMES = [QtCore.QVariant(u'記事種別'),
               QtCore.QVariant(u'記事名'),
               QtCore.QVariant(u'表示用記事名'),
               QtCore.QVariant(u'コメント'),
               QtCore.QVariant(u'時刻')]
  COL_KEYS = [u'category', u'title', u'view_title', u'comment', u'time']

  RE_LF = re.compile(r'\r?\n')

  COL_CATEGORY_INDEX = 0
  COL_TITLE_INDEX = 1

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

  def raw_row_data(self, row):
    return self.datas[row]

  def filter_id(self, row_no):
    r = self.datas[row_no]
    return u'%s%s' % (r[self.COL_CATEGORY_INDEX].toString(),
                      r[self.COL_TITLE_INDEX].toString())

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
               QtCore.QVariant(u'コミュID'),
               QtCore.QVariant(u'コミュ名'),
               QtCore.QVariant(u'生主'),
               QtCore.QVariant(u'来場数'),
               QtCore.QVariant(u'コメ数'),
               QtCore.QVariant(u'カテゴリ'),
               QtCore.QVariant(u'開始時刻')]
  COL_KEYS = [u'live_id', u'title', u'com_id', u'com_name', u'user_name', u'watcher_count', u'comment_count', u'category', u'time']

  RE_LF = re.compile(r'\r?\n')

  COL_LIVE_ID_INDEX = 0
  COL_COM_ID_INDEX = 2
  COL_COM_NAME_INDEX = 3
  COL_WATCHER_INDEX = 5
  COL_COMMENT_INDEX = 6

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

  def raw_row_data(self, row):
    return self.datas[row]

  def filter_id(self, row_no):
    # com_idでフィルタリングする
    return unicode(self.datas[row_no][self.COL_COM_ID_INDEX].toString())

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
          if d.has_key(key):
            val = d[key]
            if isinstance(val, basestring):
              str = self.RE_LF.sub('', val)
              row.append(QtCore.QVariant(QtCore.QString(str)))
            elif isinstance(val, int) or isinstance(val, datetime):
              row.append(QtCore.QVariant(val))
            elif val is None:
              row.append(QtCore.QVariant())
          else:
            row.append(QtCore.QVariant())
        self.datas.append(row)
      #self.mainWindow.trayIcon.showMessage(QtCore.QString(u'新着生放送'),
      #self.mainWindow.trayIcon.showMessage(QtCore.QString(u'新着生放送'),
      #                                     QtCore.QString(d['title']))
    finally:
      self.endInsertRows()
      self.lock.release()

class FilterListProxyModel(QtGui.QSortFilterProxyModel):
  def __init__(self, mainWindow):
    QtGui.QSortFilterProxyModel.__init__(self, mainWindow)
    self.listFilter = False

  def filterAcceptsRow(self, source_row, source_parent):
    tableModel = self.sourceModel()

    cond = False
    for i in xrange(tableModel.columnCount(None)):
      idx = tableModel.index(source_row, i, source_parent)
      cond |= tableModel.data(idx, QtCore.Qt.DisplayRole).toString().contains(self.filterRegExp())

    filter_id = tableModel.filter_id(source_row)
    return cond and (not self.listFilter or filter_id in self.list.keys())

  def setListFilter(self, bool):
    self.listFilter = bool
    self.invalidateFilter()

class DicFilterProxyModel(FilterListProxyModel):
  def __init__(self, mainWindow):
    FilterListProxyModel.__init__(self, mainWindow)
    self.list = mainWindow.watchlist

class LiveFilterProxyModel(FilterListProxyModel):
  def __init__(self, mainWindow):
    FilterListProxyModel.__init__(self, mainWindow)
    self.list = mainWindow.communityList

class WatchlistTableModel(QtCore.QAbstractTableModel):
  COL_NAMES = [QtCore.QVariant(u'カテゴリ'),
               QtCore.QVariant(u'記事名'),
               QtCore.QVariant(u'表示用記事名')]

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

  def addWatchlist(self, articles):
    if len(articles) == 0:
      return
    rowcount = len(self.datas)
    self.beginInsertRows(QtCore.QModelIndex(), rowcount, rowcount + len(articles) - 1)
    try:
      for dic_id, dic_data in articles.items():
        row = [QtCore.QVariant(QtCore.QString(dic_data['category'])),
               QtCore.QVariant(QtCore.QString(dic_data['title'])),
               QtCore.QVariant(QtCore.QString(dic_data['view_title']))]
        self.datas.append(row)
    finally:
      self.endInsertRows()

class CommunityTableModel(QtCore.QAbstractTableModel):
  COL_NAMES = [QtCore.QVariant(u'コミュID'),
               QtCore.QVariant(u'コミュ名')]

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

  def addCommunityList(self, communityList):
    if len(communityList) == 0:
      return
    rowcount = len(self.datas)
    self.beginInsertRows(QtCore.QModelIndex(), rowcount, rowcount + len(communityList) - 1)
    try:
      for com_id, com_data in communityList.items():
        row = [QtCore.QVariant(QtCore.QString(com_id)),
               QtCore.QVariant(QtCore.QString(com_data['name']))]
        self.datas.append(row)
    finally:
      self.endInsertRows()

class MainWindow(QtGui.QMainWindow):
  POLLING_DURATION = 10000 # 10000msec = 10sec
  SETTINGS_FILE_NAME = 'nicopealert.dat'

  def __init__(self, app):
    QtGui.QDialog.__init__(self)
    self.app = app

    self.ui = Ui_MainWindow()
    self.ui.setupUi(self)

    # load settings
    try:
      f = open(self.SETTINGS_FILE_NAME, 'rb')
      self.settings = pickle.load(f)
    except:
      self.settings = {'watchlist': {},
                       'communityList': {}}
    self.watchlist = self.settings['watchlist']
    self.communityList = self.settings['communityList']

    self.dicTableModel = NicoDicTableModel(self)
    self.dicFilterModel = DicFilterProxyModel(self)
    self.dicFilterModel.setSourceModel(self.dicTableModel)
    self.liveTableModel = NicoLiveTableModel(self)
    self.liveFilterModel = LiveFilterProxyModel(self)
    self.liveFilterModel.setSourceModel(self.liveTableModel)

    # watchlistTreeView
    self.watchlistTreeView = self.ui.watchlistTreeView
    self.watchlistTableModel = WatchlistTableModel(self)
    self.watchlistTreeView.setModel(self.watchlistTableModel)
    self.watchlistTreeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
    self.watchlistTreeView.setColumnWidth(0, 80)
    self.watchlistTreeView.setSortingEnabled(True)
    self.watchlistTreeView.setRootIsDecorated(False)
    self.watchlistTreeView.setAlternatingRowColors(True)
    self.watchlistTableModel.addWatchlist(self.watchlist)

    # communityTreeView
    self.communityTreeView = self.ui.communityTreeView
    self.communityTableModel = CommunityTableModel(self)
    self.communityTreeView.setModel(self.communityTableModel)
    self.communityTreeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
    self.communityTreeView.setColumnWidth(0, 80)
    self.communityTreeView.setSortingEnabled(True)
    self.communityTreeView.setRootIsDecorated(False)
    self.communityTreeView.setAlternatingRowColors(True)
    self.communityTableModel.addCommunityList(self.communityList)

    # new user tab widget !!!
    DicUserTabWidget(self)
    LiveUserTabWidget(self)

    # trayIcon/trayIconMenu/trayIconImg

    self.trayIconImg = QtGui.QIcon(self.tr('dic.ico'))
    self.trayIconMenu = QtGui.QMenu(self)
    # self.trayIconMenu.addAction(u'終了')
    self.trayIcon = QtGui.QSystemTrayIcon(self)
    self.trayIcon.setContextMenu(self.trayIconMenu)
    self.trayIcon.setIcon(self.trayIconImg)
    self.trayIcon.show()

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

  def addWatchlist(self, category, title, view_title):
    key = '%s%s' % (category, title)
    i = {key: {'category': category,
               'title': title,
               'view_title': view_title}}
    self.watchlistTableModel.addWatchlist(i)
    self.watchlist.update(i)
    self.saveSettings()

  def addCommunity(self, com_id, com_name):
    u = {com_id: {'name': com_name}}
    self.communityTableModel.addCommunityList(u)
    self.communityList.update(u)
    self.saveSettings()

  def saveSettings(self):
    try:
      f = open(self.SETTINGS_FILE_NAME, 'wb')
      pickle.dump(self.settings, f)
    except:
      pass

if __name__ == '__main__':
  import sys
  import codecs # for debug

  app = QtGui.QApplication(sys.argv)
  mw = MainWindow(app)
  mw.show()
  sys.exit(app.exec_())
