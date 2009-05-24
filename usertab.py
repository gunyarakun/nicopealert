#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
import webbrowser
import urllib

class UserTabWidget(QtGui.QWidget):
  icon = None

  def __init__(self, mainWindow, tabText, removable):
    self.mainWindow = mainWindow
    tabWidget = mainWindow.ui.tabWidget
    self.tabWidget = tabWidget
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

    # リストアイテムもしくはタブ削除ボタン
    self.removePushButton = QtGui.QPushButton(self)
    sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(self.removePushButton.sizePolicy().hasHeightForWidth())
    self.removePushButton.setSizePolicy(sizePolicy)
    self.removePushButton.setMinimumSize(QtCore.QSize(0, 16))
    self.removePushButton.setLayoutDirection(QtCore.Qt.LeftToRight)
    self.connect(self.removePushButton, QtCore.SIGNAL('clicked()'),
                 self.removeTabOrItem)
    horizontalLayout.addWidget(self.removePushButton)

    # 初期タブかどうか
    if not removable:
      self.addTabPushButton.setEnabled(False)
      self.removePushButton.setEnabled(False)

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
    tabWidget.setTabText(tabWidget.indexOf(self), self.trUtf8(tabText))
    tabWidget.setTabToolTip(tabWidget.indexOf(self), self.trUtf8(self.TAB_TOOL_TIP))
    self.listFilterCheckBox.setText(self.trUtf8(self.LIST_FILTER_CHECKBOX_TEXT))
    self.addTabPushButton.setText(self.trUtf8(self.ADD_TAB_PUSH_BUTTON_TEXT))
    self.removePushButton.setText(self.trUtf8(self.REMOVE_PUSH_BUTTON_TEXT))

  def handleContextMenu(self, point):
    tree_index = self.treeView.indexAt(point)
    filterModel_index = self.filterModel.index(tree_index.row(), 0)
    tableModel_index = self.filterModel.mapToSource(filterModel_index)

    popup_menu = QtGui.QMenu(self)
    # サブクラスで実装する。
    self.addContextMenuAction(popup_menu, tableModel_index)
    popup_menu.exec_(self.treeView.mapToGlobal(point))

  def addTab(self):
    # 現在の条件で新しいタブを作る。
    keyword = self.keywordLineEdit.text()
    check = self.listFilterCheckBox.isChecked()
    if check:
      tabText = '※' + keyword
    else:
      tabText = keyword
    newtab = self.createTab(tabText)
    newtab.keywordLineEdit.setText(self.keywordLineEdit.text())
    newtab.listFilterCheckBox.setChecked(self.listFilterCheckBox.isChecked())

  def removeTabOrItem(self):
    if self.EVENT_TAB:
      # 大百科/ニコ生タブ: タブ削除
     self.tabWidget.removeTab(self.tabWidget.indexOf(self))
    else:
      # ウォッチリスト/コミュニティリスト: 選択アイテム削除
      pass

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
    self.addTabPushButton.setEnabled(
      not self.keywordLineEdit.text().isEmpty() or
       self.listFilterCheckBox.isChecked())

class DicUserTabWidget(UserTabWidget):
  EVENT_TAB = True
  ICON_FILE_NAME = 'dic.ico'
  TAB_TOOL_TIP = 'ニコニコ大百科のイベント一覧です。'
  LIST_FILTER_CHECKBOX_TEXT = 'ウォッチリストで絞る'
  ADD_TAB_PUSH_BUTTON_TEXT = 'この条件を保存'
  REMOVE_PUSH_BUTTON_TEXT = 'このタブを削除'

  def __init__(self, mainWindow, tabText = '大百科', removable = False):
    self.tableModel = mainWindow.dicTableModel
    self.filterModel = mainWindow.dicFilterModel
    UserTabWidget.__init__(self, mainWindow, tabText, removable)

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
    menu.addAction(u'ウォッチリストに追加', lambda: self.mainWindow.addWatchlist(cat, title, view_title))

  def createTab(self, tabText):
    return DicUserTabWidget(self.mainWindow, tabText, True)

class LiveUserTabWidget(UserTabWidget):
  EVENT_TAB = True
  ICON_FILE_NAME = 'live.ico'
  TAB_TEXT = '生放送'
  TAB_TOOL_TIP = 'ニコニコ生放送のイベント一覧です。'
  LIST_FILTER_CHECKBOX_TEXT = 'コミュニティリストで絞る'
  ADD_TAB_PUSH_BUTTON_TEXT = 'この条件を保存'
  REMOVE_PUSH_BUTTON_TEXT = 'このタブを削除'

  def __init__(self, mainWindow, tabText = '生放送', removable = False):
    self.tableModel = mainWindow.liveTableModel
    self.filterModel = mainWindow.liveFilterModel
    UserTabWidget.__init__(self, mainWindow, tabText, removable)

    self.treeView.setModel(self.filterModel)
    self.treeView.hideColumn(self.tableModel.COL_COM_ID_INDEX) # 表示用じゃない記事名は隠す。

  def addContextMenuAction(self, menu, table_index):
    # FIXME: implement
    menu.addAction(u'生放送を見る', lambda: webbrowser.open(url))

  def addContextMenuAction(self, menu, table_index):
    # TODO: remove consts
    row = self.tableModel.raw_row_data(table_index.row())
    live_id = unicode(row[self.tableModel.COL_LIVE_ID_INDEX].toString())
    com_id = unicode(row[self.tableModel.COL_COM_ID_INDEX].toString())
    com_name = unicode(row[self.tableModel.COL_COM_NAME_INDEX].toString())
    url = 'http://live.nicovideo.jp/watch/' + live_id

    menu.addAction(u'生放送を見る', lambda: webbrowser.open(url))
    menu.addAction(u'URLをコピー', lambda: self.mainWindow.app.clipboard().setText(QtCore.QString(url)))
    menu.addSeparator()
    menu.addAction(u'コミュニティを通知対象にする', lambda: self.mainWindow.addCommunity(com_id, com_name))

  def createTab(self, tabText):
    return LiveUserTabWidget(self.mainWindow, tabText, True)


