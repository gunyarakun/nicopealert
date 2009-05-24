#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import threading
from datetime import datetime
from PyQt4 import QtCore, QtGui

class TableModel(QtCore.QAbstractTableModel):
  RE_LF = re.compile(r'\r?\n')

  def __init__(self, mainWindow):
    QtCore.QAbstractTableModel.__init__(self, mainWindow)
    self.mainWindow = mainWindow
    self.datas = [] # データの配列
    self.lock = threading.Lock()

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

  # これは独自メソッド。
  def raw_row_data(self, row):
    return self.datas[row]

  # これも独自。
  def appendItems(self, items):
    if len(items) == 0:
      return
    self.lock.acquire()
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
      finally:
        self.endInsertRows()
    finally:
      self.lock.release()

class NicoDicTableModel(TableModel):
  COL_NAMES = [QtCore.QVariant(u'記事種別'),
               QtCore.QVariant(u'記事名'),
               QtCore.QVariant(u'表示用記事名'),
               QtCore.QVariant(u'コメント'),
               QtCore.QVariant(u'時刻')]
  COL_KEYS = [u'category', u'title', u'view_title', u'comment', u'time']

  COL_CATEGORY_INDEX = 0
  COL_TITLE_INDEX = 1

  def filter_id(self, row_no):
    # categoryとtitleをくっつけたもの
    r = self.datas[row_no]
    return u'/%s/%s' % (r[self.COL_CATEGORY_INDEX].toString(),
                      r[self.COL_TITLE_INDEX].toString())

class NicoLiveTableModel(TableModel):
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

  COL_LIVE_ID_INDEX = 0
  COL_COM_ID_INDEX = 2
  COL_COM_NAME_INDEX = 3
  COL_WATCHER_INDEX = 5
  COL_COMMENT_INDEX = 6

  def filter_id(self, row_no):
    # com_idでフィルタリングする
    return unicode(self.datas[row_no][self.COL_COM_ID_INDEX].toString())

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
          remove_list.append(live_id)
      st_index = self.index(0, self.COL_WATCHER_INDEX)
      ed_index = self.index(len(self.datas), self.COL_COMMENT_INDEX)
      self.dataChanged(st_index, ed_index)
    finally:
      self.lock.release()

class WatchListTableModel(TableModel):
  COL_NAMES = [QtCore.QVariant(u'カテゴリ'),
               QtCore.QVariant(u'記事名'),
               QtCore.QVariant(u'表示用記事名')]
  COL_KEYS = [u'category', u'title', u'view_title']

class CommunityTableModel(TableModel):
  COL_NAMES = [QtCore.QVariant(u'コミュID'),
               QtCore.QVariant(u'コミュ名')]
  COL_KEYS = [u'id', u'name']

  COL_COM_ID_INDEX = 0
  COL_COM_NAME_INDEX = 0
