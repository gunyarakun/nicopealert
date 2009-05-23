#!/usr/bin/python
# -*- coding: utf-8 -*-

# ニコニコ大百科用アラートツール
# by Tasuku SUENAGA (a.k.a. gunyarakun)

# TODO: 検索条件の追加・保存
# TODO: カラムサイズ初期値設定
# TODO: コミュ・ウォッチリスト対象の背景色変更
# TODO: timer_handlerのスレッド化。詰まることがあるかもしれないので。
# TODO: なくなった生を削除する部分の復活。
# TODO: カラム移動・サイズの記憶
# TODO: 生ごとの詳細表示
# TODO: リファクタリング
# TODO: ネットワーク無効実験
# TODO: コミュニティ削除
# TODO: エラーハンドリング丁寧に、エラー報告ツール(ログとか)

from PyQt4 import QtCore, QtGui
from ui_mainwindow import Ui_MainWindow
from nicopoll import NicoPoll
from datetime import datetime
import threading
import webbrowser
import re
import urllib
import cPickle as pickle

class NicoDicTableModel(QtCore.QAbstractTableModel):
  COL_NAMES = [QtCore.QVariant(u'記事種別'),
               QtCore.QVariant(u'記事名'),
               QtCore.QVariant(u'表示用記事名'),
               QtCore.QVariant(u'コメント'),
               QtCore.QVariant(u'時刻')]
  COL_KEYS = [u'category', u'title', u'view_title', u'comment', u'time']

  RE_LF = re.compile(r'\r?\n')

  def __init__(self, mainWindow):
    QtCore.QAbstractTableModel.__init__(self, mainWindow)
    self.mainWindow = mainWindow
    self.datas = []
    self.ids = []

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

  def dic_id(self, row_no):
    return self.ids[row_no]

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
        self.ids.append('%s%s' % (e['category'], e['title']))
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
    self.com_ids = []
    self.com_names = []

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

  def com_id(self, row_no):
    return self.com_ids[row_no]

  def com_name(self, row_no):
    return self.com_names[row_no]

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
        self.com_ids.append(d['com_id'])
        self.com_names.append(d['com_name'])
      #self.mainWindow.trayIcon.showMessage(QtCore.QString(u'新着生放送'),
      #self.mainWindow.trayIcon.showMessage(QtCore.QString(u'新着生放送'),
      #                                     QtCore.QString(d['title']))
    finally:
      self.endInsertRows()
      self.lock.release()

class DicFilterProxyModel(QtGui.QSortFilterProxyModel):
  def __init__(self, mainWindow):
    QtGui.QSortFilterProxyModel.__init__(self, mainWindow)
    self.watchlist = mainWindow.watchlist
    self.watchlistFilter = False

  def filterAcceptsRow(self, source_row, source_parent):
    dicTableModel = self.sourceModel()

    cond = self.watchlistFilter and False in self.watchlist
    for i in xrange(dicTableModel.columnCount(None)):
      idx = dicTableModel.index(source_row, i, source_parent)
      cond |= dicTableModel.data(idx, QtCore.Qt.DisplayRole).toString().contains(self.filterRegExp())

    dic_id = dicTableModel.dic_id(source_row)
    return cond and (not self.watchlistFilter or dic_id in self.watchlist.keys())

  def setWatchlistFilter(self, bool):
    self.watchlistFilter = bool
    self.invalidateFilter()

class LiveFilterProxyModel(QtGui.QSortFilterProxyModel):
  def __init__(self, mainWindow):
    QtGui.QSortFilterProxyModel.__init__(self, mainWindow)
    self.communityList = mainWindow.communityList
    self.communityFilter = False

  def filterAcceptsRow(self, source_row, source_parent):
    liveTableModel = self.sourceModel()

    cond = False
    for i in xrange(liveTableModel.columnCount(None)):
      idx = liveTableModel.index(source_row, i, source_parent)
      cond |= liveTableModel.data(idx, QtCore.Qt.DisplayRole).toString().contains(self.filterRegExp())
    
    com_id = liveTableModel.com_id(source_row)
    return cond and (not self.communityFilter or com_id in self.communityList.keys())

  def setCommunityFilter(self, bool):
    self.communityFilter = bool
    self.invalidateFilter()

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

class UserTabWidget(QtGui.QWidget):
  icon = None

  def __init__(self, mainWindow):
    self.mainWindow = mainWindow
    tabWidget = mainWindow.ui.tabWidget
    QtGui.QWidget.__init__(self, tabWidget)

    sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
    self.setSizePolicy(sizePolicy)

    # 各種レイアウト
    gridLayout = QtGui.QGridLayout(self)
    # self.gridLayout_2.setObjectName("gridLayout_2")
    horizontalLayout = QtGui.QHBoxLayout()

    # 検索キーワード用LineEditとLabel
    label = QtGui.QLabel(self)
    label.setText(self.trUtf8('検索キーワード'))
    horizontalLayout.addWidget(label)
    self.keywordLineEdit = QtGui.QLineEdit(self)
    horizontalLayout.addWidget(self.keywordLineEdit)
    label.setBuddy(self.keywordLineEdit)
    self.connect(self.keywordLineEdit,
                 QtCore.SIGNAL('textChanged(const QString &)'),
                 self.keywordLineEditChanged)

    # リスト(ウォッチリスト/コミュニティリスト)でのフィルタCheckBox
    self.listFilterCheckBox = QtGui.QCheckBox(self)
    self.connect(self.listFilterCheckBox,
                 QtCore.SIGNAL('toggled(bool)'),
                 self.listFilterCheckBoxToggled)
    horizontalLayout.addWidget(self.listFilterCheckBox)

    # 横スペーサ
    spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
    horizontalLayout.addItem(spacerItem)

    # 指定した検索条件での新たなタブ追加ボタン
    self.addTabPushButton = QtGui.QPushButton(self)
    sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(self.addTabPushButton.sizePolicy().hasHeightForWidth())
    self.addTabPushButton.setSizePolicy(sizePolicy)
    self.addTabPushButton.setMinimumSize(QtCore.QSize(0, 16))
    self.addTabPushButton.setLayoutDirection(QtCore.Qt.LeftToRight)
    self.connect(self.addTabPushButton, QtCore.SIGNAL('clicked()'),
                 self.addTab)
    horizontalLayout.addWidget(self.addTabPushButton)

    gridLayout.addLayout(horizontalLayout, 5, 0, 1, 1)

    # イベント表示用TreeView
    self.treeView = QtGui.QTreeView(self)
    self.treeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
    self.treeView.setColumnWidth(0, 80)
    self.treeView.setSortingEnabled(True)
    self.treeView.setRootIsDecorated(False)
    self.treeView.setAlternatingRowColors(True)
    self.connect(self.treeView,
                 QtCore.SIGNAL('customContextMenuRequested(const QPoint &)'),
                 self.handleContextMenu)
    gridLayout.addWidget(self.treeView, 0, 0, 1, 1)

    # 文字列とかアイコンとか
    if self.icon is None:
      self.icon = QtGui.QIcon()
      self.icon.addPixmap(QtGui.QPixmap(self.ICON_FILE_NAME),
                          QtGui.QIcon.Normal, QtGui.QIcon.Off)

    tabWidget.addTab(self, self.icon, '')
    tabWidget.setTabText(tabWidget.indexOf(self), self.trUtf8(self.TAB_TEXT))
    tabWidget.setTabToolTip(tabWidget.indexOf(self), self.trUtf8(self.TAB_TOOL_TIP))
    self.listFilterCheckBox.setText(self.trUtf8(self.LIST_FILTER_CHECKBOX_TEXT))
    self.addTabPushButton.setText(self.trUtf8(self.ADD_TAB_PUSH_BUTTON_TEXT))

  def handleContextMenu(self, point):
    tree_index = self.treeView.indexAt(point)
    filterModel_index = self.filterModel.index(tree_index)
    tableModel_index = self.filterModel.mapToSource(filterModel_index)

    popup_menu = QtGui.QMenu(self)
    # サブクラスで実装する。
    self.addContextMenuAction(self, popup_menu, tableModel_index)
    popup_menu.exec_(self.treeView.mapToGlobal(point))

  def addTab(self):
    # TODO: 現在の条件で新しいタブを作る。
    pass

  def keywordLineEditChanged(self):
    # TODO: 検索キーワードの切り替え
    pass

  def listFilterCheckBoxToggled(self):
    # TODO: filterの切り替え
    pass


class DicUserTabWidget(UserTabWidget):
  ICON_FILE_NAME = 'dic.ico'
  TAB_TEXT = '大百科'
  TAB_TOOL_TIP = 'ニコニコ大百科のイベント一覧です。'
  LIST_FILTER_CHECKBOX_TEXT = 'ウォッチリストで絞る'
  ADD_TAB_PUSH_BUTTON_TEXT = 'この条件を保存'

  def __init__(self, mainWindow):
    self.tableModel = mainWindow.dicTableModel
    self.filterModel = mainWindow.dicFilterModel
    UserTabWidget.__init__(self, mainWindow)

    self.treeView.setModel(self.filterModel)
    self.treeView.hideColumn(1) # 表示用じゃない記事名は隠す。

  def addContextMenuAction(self, menu, table_index):
    # FIXME: implement
    menu.addAction(u'記事/掲示板を見る', lambda: webbrowser.open(url))

class LiveUserTabWidget(UserTabWidget):
  ICON_FILE_NAME = 'live.ico'
  TAB_TEXT = '生放送'
  TAB_TOOL_TIP = 'ニコニコ生放送のイベント一覧です。'
  LIST_FILTER_CHECKBOX_TEXT = 'コミュニティリストで絞る'
  ADD_TAB_PUSH_BUTTON_TEXT = 'この条件を保存'

  def __init__(self, mainWindow):
    self.tableModel = mainWindow.liveTableModel
    self.filterModel = mainWindow.liveFilterModel
    UserTabWidget.__init__(self, mainWindow)

    self.treeView.setModel(self.filterModel)

  def addContextMenuAction(self, menu, table_index):
    # FIXME: implement
    menu.addAction(u'生放送を見る', lambda: webbrowser.open(url))

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
    # 記事名カラムを隠す
    self.dicTreeView.hideColumn(1)

    self.connect(self.dicTreeView,
                 QtCore.SIGNAL('customContextMenuRequested(const QPoint &)'),
                 self.dicTreeContextMenu)

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
    self.connect(self.ui.dicWatchlistCheckBox,
                 QtCore.SIGNAL('toggled(bool)'),
                 self.dicWatchlistCheckBoxToggled)
    self.connect(self.ui.liveCommunityCheckBox,
                 QtCore.SIGNAL('toggled(bool)'),
                 self.liveWatchlistCheckBoxToggled)

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

  def dicWatchlistCheckBoxToggled(self):
    self.dicFilterModel.setWatchlistFilter(self.ui.dicWatchlistCheckBox.isChecked())

  def liveWatchlistCheckBoxToggled(self):
    self.liveFilterModel.setCommunityFilter(self.ui.liveCommunityCheckBox.isChecked())

  def dicTreeContextMenu(self, point):
    tree_index = self.dicTreeView.indexAt(point)
    dic_index = self.dicFilterModel.index(tree_index.row(), 0)
    cat = self.dicFilterModel.data(dic_index).toString()
    dic_index = self.dicFilterModel.index(tree_index.row(), 1)
    title = self.dicFilterModel.data(dic_index).toString()
    dic_index = self.dicFilterModel.index(tree_index.row(), 2)
    view_title = self.dicFilterModel.data(dic_index).toString()

    url = 'http://dic.nicovideo.jp/%s/%s' % (cat, urllib.quote(title.toUtf8()))

    popup_menu = QtGui.QMenu(self)
    popup_menu.addAction(u'記事/掲示板を見る', lambda: webbrowser.open(url))
    popup_menu.addAction(u'URLをコピー', lambda: self.app.clipboard().setText(QtCore.QString(url)))
    popup_menu.addSeparator()
    popup_menu.addAction(u'ウォッチリストに追加', lambda: self.addWatchlist(cat, title, view_title))
    popup_menu.exec_(self.dicTreeView.mapToGlobal(point))

  def liveTreeContextMenu(self, point):
    tree_index = self.liveTreeView.indexAt(point)
    live_index = self.liveFilterModel.index(tree_index.row(), 0)
    target_live_id = self.liveFilterModel.data(live_index).toString()

    model_index = self.liveFilterModel.mapToSource(live_index)
    com_id = self.liveTableModel.com_id(model_index.row())
    com_name = self.liveTableModel.com_name(model_index.row())
    url = 'http://live.nicovideo.jp/watch/' + target_live_id

    popup_menu = QtGui.QMenu(self)
    popup_menu.addAction(u'生放送を見る', lambda: webbrowser.open(url))
    popup_menu.addAction(u'URLをコピー', lambda: self.app.clipboard().setText(QtCore.QString(url)))
    popup_menu.addSeparator()
    popup_menu.addAction(u'コミュニティを通知対象にする', lambda: self.addCommunity(com_id, com_name))
    #popup_menu.addAction(u'主を通知対象にする')
    popup_menu.exec_(self.liveTreeView.mapToGlobal(point))

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
