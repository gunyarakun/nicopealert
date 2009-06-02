#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import threading
from datetime import datetime
from PyQt4 import QtCore, QtGui

# for notify
import urllib
import webbrowser

class FilterListProxyModel(QtGui.QSortFilterProxyModel):
  def __init__(self, mainWindow, tabWidget):
    QtGui.QSortFilterProxyModel.__init__(self)
    self.mainWindow = mainWindow
    self.tabWidget = tabWidget
    self.listFilter = False
    self.notify = [False, False, False]
    self.details = None # pollingされた生データが入る。

  def filterAcceptsRow(self, source_row, source_parent):
    tableModel = self.sourceModel()
    return tableModel.filterWithFilterModel(source_row, self)

  def setListFilter(self, bool):
    self.listFilter = bool
    self.invalidateFilter()

  # 各種通知がON/OFFであるというお知らせがくる。
  def setNotify(self, type, bool):
    self.notify[type] = bool
    self.mainWindow.saveTabs()

  # NOTE: Notifyの実処理を各filterModelで行わないのはなぜか。
  # それは、同じitemに対する通知が複数行われるとウザいからである。
  # 複数のfilterにひっかかっても、通知はまとめたいからね。

class DicFilterProxyModel(FilterListProxyModel):
  def __init__(self, mainWindow, tabWidget):
    FilterListProxyModel.__init__(self, mainWindow, tabWidget)
    self.list = mainWindow.settings['watchList']

class LiveFilterProxyModel(FilterListProxyModel):
  def __init__(self, mainWindow, tabWidget):
    FilterListProxyModel.__init__(self, mainWindow, tabWidget)
    self.list = mainWindow.settings['communityList']

class TableModel(QtCore.QAbstractTableModel):
  RE_LF = re.compile(r'\r?\n')

  NOTIFY_TRAY = 0
  NOTIFY_SOUND = 1
  NOTIFY_BROWSER = 2

  def __init__(self, mainWindow):
    QtCore.QAbstractTableModel.__init__(self, mainWindow)
    self.mainWindow = mainWindow
    self.datas = [] # データの配列
    self.lock = threading.Lock()
    self.targetFilterModels = []

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

  def removeRows(self, row, count, parent = QtCore.QModelIndex()):
    if count == 0:
      return False
    ret = False
    self.lock.acquire()
    try:
      end = row + count
      self.beginRemoveRows(parent, row, end - 1)
      try:
        del self.datas[row:end]
        ret = True
      finally:
        self.endRemoveRows()
    finally:
      self.lock.release()
      return ret

  # 各モデルは、QSortFilterProxyModelのソースとなるが、
  # 逆マッピングを保存しておく。通知のため。
  def addTargetFilterModel(self, model):
    self.targetFilterModels.append(model)

  # 必ず、１番目のカラムには一意なIDが入ることとする。
  def source_id(self, row_no):
    return unicode(self.datas[row_no][0].toString())

  def source_detail(self, row_no):
    return self.details[unicode(self.datas[row_no][0].toString())]

  # これは独自メソッド。
  def raw_row_data(self, row):
    return self.datas[row]

  # これも独自。
  def appendItems(self, items):
    if len(items) == 0:
      return
    self.lock.acquire()
    to_notify = [[], [], []]
    try:
      rowcount = len(self.datas)
      self.beginInsertRows(QtCore.QModelIndex(), rowcount, rowcount + len(items) - 1)
      try:
        # TODO: kにはrecordを特定できるIDが入っている。
        for k, i in items.items():
          row = []
          for key in self.COL_KEYS:
            item = QtGui.QStandardItem()
            val = i.get(key)
            if isinstance(val, basestring):
              str = self.RE_LF.sub('', val)
              row.append(QtCore.QVariant(QtCore.QString(str)))
            elif isinstance(val, int) or isinstance(val, datetime):
              row.append(QtCore.QVariant(val))
            elif val is None:
              row.append(QtCore.QVariant())
          self.datas.append(row)
          if self.FILTER_AND_NOTIFY:
            self.checkAndAddNotifyList(len(self.datas) - 1, to_notify)
      finally:
        self.endInsertRows()
      self.doNotify(to_notify)
    finally:
      self.lock.release()

  def filterWithFilterModel(self, row_no, filterModel):
    # TODO: filter対象カラムを指定する。
    cond = False
    regex = filterModel.filterRegExp()
    for col_no in xrange(0, len(self.COL_NAMES)):
      cond |= self.datas[row_no][col_no].toString().contains(regex)
    if filterModel.listFilter:
      filter_id = self.filter_id(row_no)
      return cond and filter_id in filterModel.list.keys()
    else:
      return cond

  def checkAndAddNotifyList(self, row_no, to_notify):
    n = [False, False, False]
    for fm in self.targetFilterModels:
      print fm.notify
      cond = self.filterWithFilterModel(row_no, fm)
      if cond:
        fm.tabWidget.setTabNotify(True)
        for i in xrange(0, 3): # TODO: remove const
          if fm.notify[i]:
            n[i] = True
    for i in xrange(0, 3): # TODO: remove const
      if n[i]:
        to_notify[i].append(row_no)

  def doNotify(self, to_notify):
    if to_notify[self.NOTIFY_TRAY]:
      self.notifyTray(to_notify[self.NOTIFY_TRAY])
    if to_notify[self.NOTIFY_SOUND]:
      QtGui.QSound.play('event.wav')
    if to_notify[self.NOTIFY_BROWSER]:
      self.notifyBrowser(to_notify[self.NOTIFY_BROWSER])

  def notifyTray(self, notify_list):
    pass

  def notifyBrowser(self, notify_list):
    pass

class NicoDicTableModel(TableModel):
  COL_NAMES = [QtCore.QVariant(u'ID'),
               QtCore.QVariant(u'イベント'),
               QtCore.QVariant(u'記事種別'),
               QtCore.QVariant(u'表示用記事名'),
               QtCore.QVariant(u'コメント'),
               QtCore.QVariant(u'時刻')]
  COL_KEYS = [u'dic_id', u'type_str', u'category_str', u'view_title', u'comment', u'time']

  COL_ID_INDEX = 0
  COL_TYPE_STR_INDEX = 1
  COL_CATEGORY_STR_INDEX = 2
  COL_VIEW_TITLE_INDEX = 3
  COL_COMMENT_INDEX = 4

  FILTER_AND_NOTIFY = True

  def filter_id(self, row_no):
    d = self.source_detail(row_no)
    return u'%s%s' % (d['category'], d['title'])

  def notifyTray(self, notify_list):
    vtitles = '\n'.join([unicode(self.datas[x][self.COL_VIEW_TITLE_INDEX].toString()) for x in notify_list])
    self.mainWindow.trayIcon.showMessage(self.trUtf8('新着大百科'), vtitles)

  def notifyBrowser(self, notify_list):
    d = self.source_detail(row_no)
    map(webbrowser.open,
        ['http://dic.nicovideo.jp/%s/%s' % (
          d['category'],
          urllib.quote(d['title'].encode('utf-8'))
         ) for n in notify_list])

class NicoLiveTableModel(TableModel):
  COL_NAMES = [QtCore.QVariant(u'ID'),
               QtCore.QVariant(u'タイトル'),
               QtCore.QVariant(u'コミュID'),
               QtCore.QVariant(u'コミュ名'),
               QtCore.QVariant(u'生主'),
               QtCore.QVariant(u'カテゴリ'),
               QtCore.QVariant(u'来場数'),
               QtCore.QVariant(u'コメ数'),
               QtCore.QVariant(u'詳細'),
               QtCore.QVariant(u'開始時刻')]
  COL_KEYS = [u'live_id', u'title', u'com_id', u'com_name', u'user_name', u'category', u'watcher_count', u'comment_count', u'desc', u'time']

  COL_LIVE_ID_INDEX = 0
  COL_TITLE_INDEX = 1
  COL_COM_ID_INDEX = 2
  COL_COM_NAME_INDEX = 3
  COL_WATCHER_INDEX = 6
  COL_COMMENT_INDEX = 7
  COL_DESC_INDEX = 8

  FILTER_AND_NOTIFY = True

  def filter_id(self, row_no):
    # com_idでフィルタリングする
    return self.source_detail(row_no)['com_id']

  def notifyTray(self, notify_list):
    vtitles = '\n'.join([self.source_detail(x)['title']
                         for x in notify_list])
    self.mainWindow.trayIcon.showMessage(self.trUtf8('新着生放送'), vtitles)

  def notifyBrowser(self, notify_list):
    map(webbrowser.open,
        ['http://live.nicovideo.jp/watch/%s' % self.source_id(n)
         for n in notify_list])

  def current_lives(self, lives):
    # 現在の生放送一覧から、
    # 1. 終わってしまった生放送を取り除く
    # 2. 放送中の生放送の視聴者数とコメント数を更新する

    remove_rows = []
    self.lock.acquire()
    try:
      for row in xrange(0, len(self.datas)):
        live_id = self.source_id(row)

        if lives.has_key(live_id):
          # print 'live %s count to be freshed' % live_id
          self.datas[row][self.COL_WATCHER_INDEX] = QtCore.QVariant(
            lives[live_id]['watcher_count'])
          self.datas[row][self.COL_COMMENT_INDEX] = QtCore.QVariant(
            lives[live_id]['comment_count'])
        else:
          # print 'live %s is deleted...' % (live_id)
          remove_rows.append(row)
      st_index = self.index(0, self.COL_WATCHER_INDEX)
      ed_index = self.index(len(self.datas), self.COL_COMMENT_INDEX)
      self.emit(QtCore.SIGNAL('dataChanged(const QModelIndex &, const QModelIndex &)'),
                st_index, ed_index)

      # 削除、rowがソートされていると仮定している
      for i, row in enumerate(remove_rows):
        crow = row - i # 削除によるインデックスズレを修正
        self.beginRemoveRows(QtCore.QModelIndex(), crow, crow)
        try:
          del self.datas[crow]
        finally:
          self.endRemoveRows()

      # layoutChangedをemitしたらdynamicSortFilterが効くようになったみたい。
      # いまいち挙動不明。
      self.emit(QtCore.SIGNAL('layoutChanged()'))
    finally:
      self.lock.release()

class WatchListTableModel(TableModel):
  COL_NAMES = [QtCore.QVariant(u'カテゴリ'),
               QtCore.QVariant(u'記事名'),
               QtCore.QVariant(u'表示用記事名')]
  COL_KEYS = [u'category', u'title', u'view_title']

  FILTER_AND_NOTIFY = False

class CommunityTableModel(TableModel):
  COL_NAMES = [QtCore.QVariant(u'コミュID'),
               QtCore.QVariant(u'コミュ名')]
  COL_KEYS = [u'id', u'name']

  COL_COM_ID_INDEX = 0
  COL_COM_NAME_INDEX = 0

  FILTER_AND_NOTIFY = False

