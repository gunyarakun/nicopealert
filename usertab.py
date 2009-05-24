#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib
import webbrowser
from PyQt4 import QtCore, QtGui

from models import *

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
    self.list = mainWindow.settings['watchList']

class LiveFilterProxyModel(FilterListProxyModel):
  def __init__(self, mainWindow):
    FilterListProxyModel.__init__(self, mainWindow)
    self.list = mainWindow.settings['communityList']

class UserTabWidget(QtGui.QWidget):
  icon = None

  ADD_TAB_PUSH_BUTTON_TEXT = 'この条件で新規タブ作成'
  REMOVE_COND_PUSH_BUTTON_TEXT = 'この条件をクリア'
  REMOVE_TAB_PUSH_BUTTON_TEXT = 'このタブを削除'

  def __init__(self, mainWindow, initial):
    self.mainWindow = mainWindow
    self.initial = initial
    tabWidget = mainWindow.tabWidget
    self.tabWidget = tabWidget
    QtGui.QWidget.__init__(self, tabWidget)

    sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
    self.setSizePolicy(sizePolicy)

    # 各種レイアウト
    gridLayout = QtGui.QGridLayout(self)
    horizontalLayout = QtGui.QHBoxLayout()

    # 検索キーワード/リスト追加用LineEditとLabel
    label = QtGui.QLabel(self)
    horizontalLayout.addWidget(label)
    self.keywordLineEdit = QtGui.QLineEdit(self)
    label.setBuddy(self.keywordLineEdit)
    horizontalLayout.addWidget(self.keywordLineEdit)

    if self.EVENT_TAB:
      label.setText(self.trUtf8('検索キーワード'))
      self.connect(self.keywordLineEdit,
                   QtCore.SIGNAL('textChanged(const QString &)'),
                   self.keywordLineEditChanged)

      # リスト(ウォッチリスト/コミュニティリスト)でのフィルタCheckBox
      self.listFilterCheckBox = QtGui.QCheckBox(self)
      self.listFilterCheckBox.setText(self.trUtf8(self.LIST_FILTER_CHECKBOX_TEXT))
      self.connect(self.listFilterCheckBox,
                   QtCore.SIGNAL('toggled(bool)'),
                   self.listFilterCheckBoxToggled)
      horizontalLayout.addWidget(self.listFilterCheckBox)
    else:
      label.setText(self.trUtf8(self.LINE_EDIT_LABEL))

    # 横スペーサ
    spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
    horizontalLayout.addItem(spacerItem)

    # リストアイテムもしくは指定した検索条件での新たなタブ追加ボタン
    self.addPushButton = QtGui.QPushButton(self)
    sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(self.addPushButton.sizePolicy().hasHeightForWidth())
    self.addPushButton.setSizePolicy(sizePolicy)
    self.addPushButton.setMinimumSize(QtCore.QSize(0, 16))
    self.addPushButton.setLayoutDirection(QtCore.Qt.LeftToRight)
    if self.EVENT_TAB:
      self.addPushButton.setText(self.trUtf8(self.ADD_TAB_PUSH_BUTTON_TEXT))
    else:
      self.addPushButton.setText(self.trUtf8(self.ADD_ITEM_PUSH_BUTTON_TEXT))
    self.connect(self.addPushButton, QtCore.SIGNAL('clicked()'),
                 self.addTabOrItem)
    horizontalLayout.addWidget(self.addPushButton)

    # リストアイテムもしくはタブもしくは条件削除ボタン
    self.removePushButton = QtGui.QPushButton(self)
    sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(self.removePushButton.sizePolicy().hasHeightForWidth())
    self.removePushButton.setSizePolicy(sizePolicy)
    self.removePushButton.setMinimumSize(QtCore.QSize(0, 16))
    self.removePushButton.setLayoutDirection(QtCore.Qt.LeftToRight)
    if self.EVENT_TAB:
      if initial:
        self.removePushButton.setText(self.trUtf8(self.REMOVE_COND_PUSH_BUTTON_TEXT))
      else:
        self.removePushButton.setText(self.trUtf8(self.REMOVE_TAB_PUSH_BUTTON_TEXT))
    else:
      self.removePushButton.setText(self.trUtf8(self.REMOVE_ITEM_PUSH_BUTTON_TEXT))
    self.connect(self.removePushButton, QtCore.SIGNAL('clicked()'),
                 self.removeTabOrItem)
    horizontalLayout.addWidget(self.removePushButton)

    #
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
    tabWidget.setTabToolTip(tabWidget.indexOf(self), self.trUtf8(self.TAB_TOOL_TIP))

    # 追加ボタンの状態を更新
    self.updateAddButton()

  def handleContextMenu(self, point):
    tree_index = self.treeView.indexAt(point)
    filterModel_index = self.filterModel.index(tree_index.row(), 0)
    tableModel_index = self.filterModel.mapToSource(filterModel_index)

    popup_menu = QtGui.QMenu(self)
    # サブクラスで実装する。
    self.addContextMenuAction(popup_menu, tableModel_index)
    popup_menu.exec_(self.treeView.mapToGlobal(point))

  def addTabOrItem(self):
    # 現在の条件で新しいタブを作り、そこにフォーカスをうつす。
    keyword = self.keywordLineEdit.text()
    check = self.listFilterCheckBox.isChecked()
    newtab = self.createTab()
    newtab.keywordLineEdit.setText(keyword)
    newtab.listFilterCheckBox.setChecked(check)
    self.tabWidget.setCurrentIndex(self.tabWidget.indexOf(newtab))
    self.clearCond()

  def clearCond(self):
    self.keywordLineEdit.setText('')
    self.listFilterCheckBox.setChecked(False)

  def removeTabOrItem(self):
    if self.EVENT_TAB:
      # 大百科/ニコ生タブ
      if self.initial:
        # 初期タブ: 条件クリア
        self.clearCond()
      else:
        # 追加タブ: タブ削除
        self.tabWidget.removeTab(self.tabWidget.indexOf(self))
    else:
      # ウォッチリスト/コミュニティリスト: 選択アイテム削除
      for idx in self.treeView.selectedIndexes():
        self.filterModel.removeRows(idx.row(), 1)
      # TODO: モデル側で、削除したものをsettingsから消す。

  def keywordLineEditChanged(self):
    # 検索キーワードの切り替え
    regex = QtCore.QRegExp(self.keywordLineEdit.text(),
                           QtCore.Qt.CaseInsensitive,
                           QtCore.QRegExp.RegExp2)
    self.filterModel.setFilterRegExp(regex)
    self.updateAddButton()

  def listFilterCheckBoxToggled(self):
    # ウォッチリスト/コミュニティリストでの絞込をするかどうか切り替え
    self.filterModel.setListFilter(self.listFilterCheckBox.isChecked())
    self.updateAddButton()

  def updateAddButton(self):
    if self.EVENT_TAB:
      keyword = self.keywordLineEdit.text()

      self.addPushButton.setEnabled(
        self.initial and (
          not keyword.isEmpty() or
          self.listFilterCheckBox.isChecked()
        )
      )

      if keyword.isEmpty():
        keyword = self.DEFAULT_TAB_TEXT
      else:
        keyword = keyword.toUtf8()

      if self.listFilterCheckBox.isChecked():
        tabText = '※' + keyword
      else:
        tabText = keyword
      self.tabWidget.setTabText(self.tabWidget.indexOf(self),
                                self.trUtf8(tabText))
    else:
      self.tabWidget.setTabText(self.tabWidget.indexOf(self),
                                self.trUtf8(self.DEFAULT_TAB_TEXT))

class DicUserTabWidget(UserTabWidget):
  EVENT_TAB = True
  ICON_FILE_NAME = 'dic.ico'
  DEFAULT_TAB_TEXT = '大百科'
  TAB_TOOL_TIP = 'ニコニコ大百科のイベント一覧です。'
  LIST_FILTER_CHECKBOX_TEXT = 'ウォッチリストで絞る'

  def __init__(self, mainWindow, initial = True):
    self.tableModel = mainWindow.dicTableModel
    self.filterModel = DicFilterProxyModel(mainWindow)
    self.filterModel.setSourceModel(self.tableModel)
    UserTabWidget.__init__(self, mainWindow, initial)

    self.treeView.setModel(self.filterModel)
    self.treeView.hideColumn(self.tableModel.COL_TITLE_INDEX) # 表示用じゃない記事名は隠す。

  def addContextMenuAction(self, menu, table_index):
    cat, title, view_title = \
      map(lambda d: unicode(d.toString()),
          self.tableModel.raw_row_data(table_index.row())[0:3])
    url = 'http://dic.nicovideo.jp/%s/%s' % (cat, urllib.quote(title.encode('utf-8')))

    menu.addAction(u'記事/掲示板を見る', lambda: webbrowser.open(url))
    menu.addAction(u'URLをコピー', lambda: self.mainWindow.app.clipboard().setText(QtCore.QString(url)))
    menu.addSeparator()
    menu.addAction(u'ウォッチリストに追加', lambda: self.mainWindow.addWatchList(cat, title, view_title))

  def createTab(self):
    return DicUserTabWidget(self.mainWindow, False)

class LiveUserTabWidget(UserTabWidget):
  EVENT_TAB = True
  ICON_FILE_NAME = 'live.ico'
  DEFAULT_TAB_TEXT = '生放送'
  TAB_TOOL_TIP = 'ニコニコ生放送のイベント一覧です。'
  LIST_FILTER_CHECKBOX_TEXT = 'コミュニティリストで絞る'

  def __init__(self, mainWindow, initial = True):
    self.tableModel = mainWindow.liveTableModel
    self.filterModel = LiveFilterProxyModel(mainWindow)
    self.filterModel.setSourceModel(self.tableModel)
    UserTabWidget.__init__(self, mainWindow, initial)

    self.treeView.setModel(self.filterModel)
    self.treeView.hideColumn(self.tableModel.COL_COM_ID_INDEX) # 表示用じゃない記事名は隠す。

  def addContextMenuAction(self, menu, table_index):
    row = self.tableModel.raw_row_data(table_index.row())
    live_id = unicode(row[self.tableModel.COL_LIVE_ID_INDEX].toString())
    com_id = unicode(row[self.tableModel.COL_COM_ID_INDEX].toString())
    com_name = unicode(row[self.tableModel.COL_COM_NAME_INDEX].toString())
    url = 'http://live.nicovideo.jp/watch/' + live_id

    menu.addAction(u'生放送を見る', lambda: webbrowser.open(url))
    menu.addAction(u'URLをコピー', lambda: self.mainWindow.app.clipboard().setText(QtCore.QString(url)))
    menu.addSeparator()
    menu.addAction(u'コミュニティを通知対象にする', lambda: self.mainWindow.addCommunity(com_id, com_name))

  def createTab(self):
    return LiveUserTabWidget(self.mainWindow, False)

class WatchListUserTabWidget(UserTabWidget):
  EVENT_TAB = False
  ICON_FILE_NAME = 'dic.ico'
  DEFAULT_TAB_TEXT = 'ウォッチリスト'
  TAB_TOOL_TIP = 'イベントを知りたい大百科の記事一覧です。'
  LINE_EDIT_LABEL = '追加したい記事のURL'
  ADD_ITEM_PUSH_BUTTON_TEXT = 'ウォッチリスト追加'
  REMOVE_ITEM_PUSH_BUTTON_TEXT = 'ウォッチリスト削除'

  def __init__(self, mainWindow, initial = True):
    self.tableModel = mainWindow.watchListTableModel
    self.filterModel = QtGui.QSortFilterProxyModel(mainWindow)
    self.filterModel.setSourceModel(self.tableModel)
    UserTabWidget.__init__(self, mainWindow, initial)

    self.treeView.setModel(self.filterModel)

  def addContextMenuAction(self, menu, table_index):
    # FIXME: implement!!!!!
    row = self.tableModel.raw_row_data(table_index.row())
    live_id = unicode(row[self.tableModel.COL_LIVE_ID_INDEX].toString())
    com_id = unicode(row[self.tableModel.COL_COM_ID_INDEX].toString())
    com_name = unicode(row[self.tableModel.COL_COM_NAME_INDEX].toString())
    url = 'http://live.nicovideo.jp/watch/' + live_id

    menu.addAction(u'ページを見る', lambda: webbrowser.open(url))
    menu.addAction(u'URLをコピー', lambda: self.mainWindow.app.clipboard().setText(QtCore.QString(url)))
    menu.addSeparator()
    menu.addAction(u'削除する', lambda: self.mainWindow.addCommunity(com_id, com_name))

class CommunityListUserTabWidget(UserTabWidget):
  EVENT_TAB = False
  ICON_FILE_NAME = 'live.ico'
  DEFAULT_TAB_TEXT = 'コミュリスト'
  TAB_TOOL_TIP = 'イベントを知りたいコミュニティの一覧です。'
  LINE_EDIT_LABEL = '追加したいコミュニティ(空白区切り)'
  ADD_ITEM_PUSH_BUTTON_TEXT = 'コミュ追加'
  REMOVE_ITEM_PUSH_BUTTON_TEXT = 'コミュ削除'

  def __init__(self, mainWindow, initial = True):
    self.tableModel = mainWindow.communityListTableModel
    self.filterModel = QtGui.QSortFilterProxyModel(mainWindow)
    self.filterModel.setSourceModel(self.tableModel)
    UserTabWidget.__init__(self, mainWindow, initial)

    self.treeView.setModel(self.filterModel)

  def addContextMenuAction(self, menu, table_index):
    # FIXME: implement!!!!!
    row = self.tableModel.raw_row_data(table_index.row())
    live_id = unicode(row[self.tableModel.COL_LIVE_ID_INDEX].toString())
    com_id = unicode(row[self.tableModel.COL_COM_ID_INDEX].toString())
    com_name = unicode(row[self.tableModel.COL_COM_NAME_INDEX].toString())
    url = 'http://live.nicovideo.jp/watch/' + live_id

    menu.addAction(u'ページを見る', lambda: webbrowser.open(url))
    menu.addAction(u'URLをコピー', lambda: self.mainWindow.app.clipboard().setText(QtCore.QString(url)))
    menu.addSeparator()
    menu.addAction(u'削除する', lambda: self.mainWindow.addCommunity(com_id, com_name))
