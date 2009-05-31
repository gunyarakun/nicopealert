#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import urllib
import webbrowser
from PyQt4 import QtCore, QtGui

import urllib2 # コミュ画像取得のため
import cgi # エスケープ

from models import *

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

    self.tableModel.addTargetFilterModel(self.filterModel)

    sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
    self.setSizePolicy(sizePolicy)

    # デフォルトのタブ文字色を保存しておく
    self.textColor = tabWidget.tabBar().tabTextColor(tabWidget.indexOf(self))

    # 各種レイアウト
    gridLayout = QtGui.QGridLayout(self)
    horizontalLayout = QtGui.QHBoxLayout()

    # 通知系
    if self.EVENT_TAB:
      # システムトレイで通知
      self.trayNotifyCheckBox = QtGui.QCheckBox(self)
      self.trayNotifyCheckBox.setText(self.trUtf8('文'))
      self.connect(self.trayNotifyCheckBox,
                   QtCore.SIGNAL('toggled(bool)'),
                   lambda: self.filterModel.setNotify(self.tableModel.NOTIFY_TRAY,
                                                      self.trayNotifyCheckBox.isChecked()))
      horizontalLayout.addWidget(self.trayNotifyCheckBox)

      # 音
      self.soundNotifyCheckBox = QtGui.QCheckBox(self)
      self.soundNotifyCheckBox.setText(self.trUtf8('音'))
      self.connect(self.soundNotifyCheckBox,
                   QtCore.SIGNAL('toggled(bool)'),
                   lambda: self.filterModel.setNotify(self.tableModel.NOTIFY_SOUND,
                                                      self.trayNotifyCheckBox.isChecked()))
      horizontalLayout.addWidget(self.soundNotifyCheckBox)

      # 自動open
      self.browserNotifyCheckBox = QtGui.QCheckBox(self)
      self.browserNotifyCheckBox.setText(self.trUtf8('閲'))
      self.connect(self.browserNotifyCheckBox,
                   QtCore.SIGNAL('toggled(bool)'),
                   lambda: self.filterModel.setNotify(self.tableModel.NOTIFY_BROWSER,
                                                      self.trayNotifyCheckBox.isChecked()))
      horizontalLayout.addWidget(self.browserNotifyCheckBox)

    # 横スペーサ
    spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
    horizontalLayout.addItem(spacerItem)

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

    # イベント表示用TreeView
    self.treeView = QtGui.QTreeView(self)
    self.treeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
    self.treeView.setSortingEnabled(True)
    self.treeView.setRootIsDecorated(False)
    self.treeView.setAlternatingRowColors(True)
    self.treeView.setItemsExpandable(False)
    self.connect(self.treeView,
                 QtCore.SIGNAL('customContextMenuRequested(const QPoint &)'),
                 self.handleContextMenu)

    # サムネイル・詳細情報表示用
    detailHBox = QtGui.QHBoxLayout()

    # サムネイル表示用
    self.thumbLabel = QtGui.QLabel()
    detailHBox.addWidget(self.thumbLabel)

    # 詳細情報表示用QTextBrowser
    self.textBrowser = QtGui.QTextBrowser()
    self.textBrowser.setMaximumHeight(128)
    self.textBrowser.setOpenLinks(False)
    self.connect(self.textBrowser,
                 QtCore.SIGNAL('anchorClicked(const QUrl &)'),
                 self.anchorClickedHandler)
    detailHBox.addWidget(self.textBrowser)

    # タブの中身を作成
    gridLayout.addWidget(self.treeView, 0, 0)
    gridLayout.addLayout(detailHBox, 1, 0)
    gridLayout.addLayout(horizontalLayout, 2, 0)

    # 文字列とかアイコンとか
    if self.icon is None:
      self.icon = QtGui.QIcon()
      self.icon.addPixmap(QtGui.QPixmap(self.ICON_FILE_NAME),
                          QtGui.QIcon.Normal, QtGui.QIcon.Off)

    tabWidget.addTab(self, self.icon, '')
    tabWidget.setTabToolTip(tabWidget.indexOf(self), self.trUtf8(self.TAB_TOOL_TIP))

    # 追加ボタンの状態を更新
    self.updateAddButton()

    # ダイナミックソートを有効に
    self.filterModel.setDynamicSortFilter(True)

  def init_after_show(self):
    # Qtの制限？で、Tab内のWidgetで最初のタブ以外のものについては
    # カラムの削除やリサイズができない。
    # showのあとなら出来るっぽい？ので
    self.treeView.setModel(self.filterModel)
    self.connect(self.treeView.selectionModel(),
                 QtCore.SIGNAL('currentChanged(' \
                                 'const QModelIndex &, ' \
                                 'const QModelIndex &)'),
                 self.currentChangedHandler)

  def getTableIndexFromTreeViewIndex(self, treeViewIndex):
    filterModel_index = self.filterModel.index(treeViewIndex.row(), 0)
    return self.filterModel.mapToSource(filterModel_index)

  def anchorClickedHandler(self, qurl):
    webbrowser.open(qurl.toString())

  def currentChangedHandler(self, current, prev):
    table_index = self.filterModel.mapToSource(current)
    self.currentChangedHandlerRow(table_index)

  def currentChangedHandlerRow(self, table_index):
    # サブクラスで実装する。
    pass

  def setCond(self, cond):
    keyword = QtCore.QString(cond['keyword'])
    self.keywordLineEdit.setText(keyword)
    self.listFilterCheckBox.setChecked(cond['isListFilter'])
    self.trayNotifyCheckBox.setChecked(cond['isTrayNotify'])
    self.soundNotifyCheckBox.setChecked(cond['isSoundNotify'])
    self.browserNotifyCheckBox.setChecked(cond['isBrowserNotify'])

  def cond(self):
    return {
      'class': unicode(self.__class__.__name__),
      'keyword': unicode(self.keywordLineEdit.text()),
      'isListFilter': self.listFilterCheckBox.isChecked(),
      'isTrayNotify': self.trayNotifyCheckBox.isChecked(),
      'isSoundNotify': self.soundNotifyCheckBox.isChecked(),
      'isBrowserNotify': self.browserNotifyCheckBox.isChecked()
    }

  def clearCond(self):
    self.setCond({
      'keyword': u'',
      'isListFilter': False,
      'isTrayNotify': False,
      'isSoundNotify': False,
      'isBrowserNotify': False,
      })

  def handleContextMenu(self, point):
    tree_index = self.treeView.indexAt(point)
    row = self.getTableIndexFromTreeViewIndex(tree_index)

    popup_menu = QtGui.QMenu(self)
    # サブクラスで実装する。
    self.addContextMenuAction(popup_menu, row)
    popup_menu.exec_(self.treeView.mapToGlobal(point))

  def addTabOrItem(self):
    if self.EVENT_TAB:
      # 現在の条件で新しいタブを作り、そこにフォーカスをうつす。
      newtab = self.createTab()
      newtab.setCond(self.cond())
      self.tabWidget.setCurrentIndex(self.tabWidget.indexOf(newtab))
      self.clearCond()
      newtab.init_after_show()
      self.mainWindow.saveTabs()
    else:
      # リストの要素を追加する
      keyword = unicode(self.keywordLineEdit.text())
      for i in keyword.split():
        self.addItem(i)
      self.keywordLineEdit.setText('')

  def removeTabOrItem(self):
    if self.EVENT_TAB:
      # 大百科/ニコ生タブ
      if self.initial:
        # 初期タブ: 条件クリア
        self.clearCond()
      else:
        # 追加タブ: タブ削除
        self.tabWidget.removeTab(self.tabWidget.indexOf(self))
        self.mainWindow.saveTabs()
    else:
      # ウォッチリスト/コミュニティリスト: 選択アイテム削除
      idxs = self.treeView.selectedIndexes()
      if len(idxs) >= 1:
        # NOTE: removeItemについては設計が汚い。修正すべき。
        self.removeItem(idxs[0].row())

  def keywordLineEditChanged(self):
    # 検索キーワードの切り替え
    regex = QtCore.QRegExp(self.keywordLineEdit.text(),
                           QtCore.Qt.CaseInsensitive,
                           QtCore.QRegExp.RegExp2)
    self.filterModel.setFilterRegExp(regex)
    self.updateAddButton()
    if not self.initial:
      self.mainWindow.saveTabs()

  def listFilterCheckBoxToggled(self):
    # ウォッチリスト/コミュニティリストでの絞込をするかどうか切り替え
    self.filterModel.setListFilter(self.listFilterCheckBox.isChecked())
    self.updateAddButton()
    if not self.initial:
      self.mainWindow.saveTabs()

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

  # イベントが起こったので、タブの文字色を変えてみる
  def setTabNotify(self, bool):
    tabBar = self.tabWidget.tabBar()
    index = self.tabWidget.indexOf(self)
    if bool and tabBar.currentIndex() != index:
      color = QtGui.QColor('#ff0000')
    else:
      color = self.textColor
    tabBar.setTabTextColor(index, color)

class DicUserTabWidget(UserTabWidget):
  EVENT_TAB = True
  ICON_FILE_NAME = ':/dic.ico'
  DEFAULT_TAB_TEXT = '大百科'
  TAB_TOOL_TIP = 'ニコニコ大百科のイベント一覧です。'
  LIST_FILTER_CHECKBOX_TEXT = 'ウォッチリストで絞る'

  def __init__(self, mainWindow, initial = True):
    self.tableModel = mainWindow.dicTableModel
    self.filterModel = DicFilterProxyModel(mainWindow, self)
    self.filterModel.setSourceModel(self.tableModel)
    UserTabWidget.__init__(self, mainWindow, initial)

  def init_after_show(self):
    UserTabWidget.init_after_show(self)
    # TODO: refactoring
    header = self.treeView.header()
    header.setSectionHidden(self.tableModel.COL_CATEGORY_INDEX, True)
    header.setSectionHidden(self.tableModel.COL_TITLE_INDEX, True)
    header.setSectionHidden(self.tableModel.COL_REV_ID_INDEX, True)
    header.setSectionHidden(self.tableModel.COL_RES_NO_INDEX, True)
    header.setSectionHidden(self.tableModel.COL_OEKAKI_ID_INDEX, True)
    header.setSectionHidden(self.tableModel.COL_OEKAKI_TITLE_INDEX, True)
    header.setSectionHidden(self.tableModel.COL_MML_ID_INDEX, True)
    header.setSectionHidden(self.tableModel.COL_MML_TITLE_INDEX, True)

    header.setStretchLastSection(False)
    header.resizeSection(self.tableModel.COL_CATEGORY_STR_INDEX, 30)
    header.resizeSection(self.tableModel.COL_VIEW_TITLE_INDEX, 150)
    header.resizeSection(self.tableModel.COL_TYPE_STR_INDEX, 40)
    header.resizeSection(12, 110)

    header.setResizeMode(self.tableModel.COL_CATEGORY_STR_INDEX, QtGui.QHeaderView.Fixed)
    header.setResizeMode(self.tableModel.COL_VIEW_TITLE_INDEX, QtGui.QHeaderView.Interactive)
    header.setResizeMode(self.tableModel.COL_TYPE_STR_INDEX, QtGui.QHeaderView.Fixed)
    header.setResizeMode(self.tableModel.COL_COMMENT_INDEX, QtGui.QHeaderView.Stretch)
    header.setResizeMode(12, QtGui.QHeaderView.Fixed)

  def currentChangedHandlerRow(self, table_index):
    row = self.tableModel.raw_row_data(table_index.row())
    oekaki_id, ok = row[self.tableModel.COL_OEKAKI_ID_INDEX].toInt()
    comment = unicode(row[self.tableModel.COL_COMMENT_INDEX].toString())
    if ok:
      pixmap = QtGui.QPixmap()
      img_url = 'http://dic.nicovideo.jp/oekaki_thumb/%d.png' % oekaki_id
      try:
        img = urllib2.urlopen(img_url).read()
        pixmap.loadFromData(img)
      except urllib2.HTTPError:
        pass
      self.thumbLabel.setPixmap(pixmap)
    else:
      self.thumbLabel.clear()

    html = cgi.escape(comment)
    html = self.tableModel.RE_LF.sub('<br>', html)

    self.textBrowser.setHtml(html)

  def addContextMenuAction(self, menu, table_index):
    cat, title, view_title = \
      map(lambda d: unicode(d.toString()),
          self.tableModel.raw_row_data(table_index.row())[0:3])
    url = 'http://dic.nicovideo.jp/%s/%s' % (cat, urllib.quote(title.encode('utf-8')))

    menu.addAction(u'記事/掲示板を見る', lambda: webbrowser.open(url))
    menu.addAction(u'URLをコピー', lambda: self.mainWindow.app.clipboard().setText(QtCore.QString(url)))
    menu.addSeparator()
    menu.addAction(u'ウォッチリストに追加', lambda: self.mainWindow.appendWatchList(cat, title, view_title))

  def createTab(self):
    return DicUserTabWidget(self.mainWindow, False)

class LiveUserTabWidget(UserTabWidget):
  EVENT_TAB = True
  ICON_FILE_NAME = ':/live.ico'
  DEFAULT_TAB_TEXT = '生放送'
  TAB_TOOL_TIP = 'ニコニコ生放送のイベント一覧です。'
  LIST_FILTER_CHECKBOX_TEXT = 'コミュリストで絞る'

  def __init__(self, mainWindow, initial = True):
    self.tableModel = mainWindow.liveTableModel
    self.filterModel = LiveFilterProxyModel(mainWindow, self)
    self.filterModel.setSourceModel(self.tableModel)
    UserTabWidget.__init__(self, mainWindow, initial)

  def init_after_show(self):
    UserTabWidget.init_after_show(self)
    # TODO: refactoring
    header = self.treeView.header()
    header.setStretchLastSection(False)
    header.setSectionHidden(self.tableModel.COL_LIVE_ID_INDEX, True)
    header.setSectionHidden(self.tableModel.COL_COM_ID_INDEX, True)
    header.setSectionHidden(self.tableModel.COL_DESC_INDEX, True)
    header.resizeSection(1, 200)
    header.resizeSection(3, 120)
    header.resizeSection(4, 60)
    header.resizeSection(5, 70)
    header.resizeSection(6, 40)
    header.resizeSection(7, 40)
    header.resizeSection(9, 110)
    header.setResizeMode(1, QtGui.QHeaderView.Interactive)
    header.setResizeMode(3, QtGui.QHeaderView.Interactive)
    header.setResizeMode(4, QtGui.QHeaderView.Interactive)
    header.setResizeMode(5, QtGui.QHeaderView.Stretch)
    header.setResizeMode(6, QtGui.QHeaderView.Fixed)
    header.setResizeMode(7, QtGui.QHeaderView.Fixed)
    header.setResizeMode(9, QtGui.QHeaderView.Fixed)

  def currentChangedHandlerRow(self, table_index):
    row = self.tableModel.raw_row_data(table_index.row())
    com_id = unicode(row[self.tableModel.COL_COM_ID_INDEX].toString())
    desc = unicode(row[self.tableModel.COL_DESC_INDEX].toString())
    if com_id[0:2] == u'co':
      img_url = u'http://icon.nicovideo.jp/community/%s.jpg' % com_id
    elif com_id[0:2] == u'ch':
      img_url = u'http://icon.nicovideo.jp/channel/%s.jpg' % com_id

    pixmap = QtGui.QPixmap(128, 128)
    try:
      img = urllib2.urlopen(img_url).read()
      pixmap.loadFromData(img)
    except urllib2.HTTPError:
      pass
    finally:
      self.thumbLabel.setPixmap(pixmap)

    self.textBrowser.setHtml(desc)

  def addContextMenuAction(self, menu, table_index):
    row = self.tableModel.raw_row_data(table_index.row())
    live_id = unicode(row[self.tableModel.COL_LIVE_ID_INDEX].toString())
    com_id = unicode(row[self.tableModel.COL_COM_ID_INDEX].toString())
    com_name = unicode(row[self.tableModel.COL_COM_NAME_INDEX].toString())
    url = 'http://live.nicovideo.jp/watch/' + live_id

    menu.addAction(u'生放送を見る', lambda: webbrowser.open(url))
    menu.addAction(u'URLをコピー', lambda: self.mainWindow.app.clipboard().setText(QtCore.QString(url)))
    menu.addSeparator()
    menu.addAction(u'コミュニティを通知対象にする', lambda: self.mainWindow.appendCommunityList(com_id, com_name))

  def createTab(self):
    return LiveUserTabWidget(self.mainWindow, False)

class WatchListUserTabWidget(UserTabWidget):
  EVENT_TAB = False
  ICON_FILE_NAME = ':/dic.ico'
  DEFAULT_TAB_TEXT = 'ウォッチリスト'
  TAB_TOOL_TIP = 'イベントを知りたい大百科の記事一覧です。'
  LINE_EDIT_LABEL = '追加したい記事のURL'
  ADD_ITEM_PUSH_BUTTON_TEXT = 'ウォッチリスト追加'
  REMOVE_ITEM_PUSH_BUTTON_TEXT = 'ウォッチリスト削除'

  URL_REGEX = re.compile(r'^(http://dic.nicovideo.jp)?(/b)?/([aviuc])/([^/]+)')

  def __init__(self, mainWindow, initial = True):
    self.tableModel = mainWindow.watchListTableModel
    self.filterModel = QtGui.QSortFilterProxyModel(mainWindow)
    self.filterModel.setSourceModel(self.tableModel)
    UserTabWidget.__init__(self, mainWindow, initial)

  def addContextMenuAction(self, menu, table_index):
    cat, title, view_title = \
      map(lambda d: unicode(d.toString()),
          self.tableModel.raw_row_data(table_index.row())[0:3])
    url = 'http://dic.nicovideo.jp/%s/%s' % (cat, urllib.quote(title.encode('utf-8')))

    menu.addAction(u'ページを見る', lambda: webbrowser.open(url))
    menu.addAction(u'URLをコピー', lambda: self.mainWindow.app.clipboard().setText(QtCore.QString(url)))
    menu.addSeparator()
    menu.addAction(u'削除する', lambda: self.mainWindow.removeWatchList(table_index.row()))

  def addItem(self, url):
    m = self.URL_REGEX.match(url)
    if m:
      category = m.group(3)
      title = urllib.unquote(m.group(4)).encode('raw_unicode_escape').decode('utf-8')
      # TODO: 表示用記事名を取得する
      self.mainWindow.appendWatchList(category, title, None)

  def removeItem(self, index):
    self.mainWindow.removeWatchList(index)

class CommunityListUserTabWidget(UserTabWidget):
  EVENT_TAB = False
  ICON_FILE_NAME = ':/live.ico'
  DEFAULT_TAB_TEXT = 'コミュリスト'
  TAB_TOOL_TIP = 'イベントを知りたいコミュニティの一覧です。'
  LINE_EDIT_LABEL = '追加したいコミュニティID(空白区切り)'
  ADD_ITEM_PUSH_BUTTON_TEXT = 'コミュ追加'
  REMOVE_ITEM_PUSH_BUTTON_TEXT = 'コミュ削除'

  def __init__(self, mainWindow, initial = True):
    self.tableModel = mainWindow.communityListTableModel
    self.filterModel = QtGui.QSortFilterProxyModel(mainWindow)
    self.filterModel.setSourceModel(self.tableModel)
    UserTabWidget.__init__(self, mainWindow, initial)

  def addContextMenuAction(self, menu, table_index):
    row = self.tableModel.raw_row_data(table_index.row())
    com_id = unicode(row[self.tableModel.COL_COM_ID_INDEX].toString())
    com_name = unicode(row[self.tableModel.COL_COM_NAME_INDEX].toString())
    url = 'http://ch.nicovideo.jp/community/' + com_id

    menu.addAction(u'ページを見る', lambda: webbrowser.open(url))
    menu.addAction(u'URLをコピー', lambda: self.mainWindow.app.clipboard().setText(QtCore.QString(url)))
    menu.addSeparator()
    menu.addAction(u'削除する', lambda: self.mainWindow.removeCommunityList(table_index.row()))

  def addItem(self, com_id):
    self.mainWindow.appendCommunityList(com_id, None)

  def removeItem(self, index):
    self.mainWindow.removeCommunityList(index)
