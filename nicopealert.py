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
# TODO: 新着イベントでタブ色変更
# TODO: コミュ・ウォッチリスト対象の背景色変更
# TODO: timer_handlerのスレッド化。詰まることがあるかもしれないので。
# TODO: なくなった生を削除する部分の復活。
# TODO: 生ごとの詳細表示
# TODO: リファクタリング
# TODO: ネットワーク無効実験
# TODO: エラーハンドリング丁寧に、エラー報告ツール(ログとか)

from PyQt4 import QtCore, QtGui
from ui_mainwindow import Ui_MainWindow
import cPickle as pickle

from nicopoll import NicoPoll
from usertab import *
from models import *

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
      self['watchList']
      self['communityList']
    except:
      self.settings = {'watchList': {},
                       'communityList': {}}

    self.dicTableModel = NicoDicTableModel(self)
    self.liveTableModel = NicoLiveTableModel(self)

    # watchListTreeView
    self.watchListTreeView = self.ui.watchListTreeView
    self.watchListTableModel = WatchListTableModel(self)
    self.watchListTreeView.setModel(self.watchListTableModel)
    self.watchListTreeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
    self.watchListTreeView.setColumnWidth(0, 80)
    self.watchListTreeView.setSortingEnabled(True)
    self.watchListTreeView.setRootIsDecorated(False)
    self.watchListTreeView.setAlternatingRowColors(True)
    self.watchListTableModel.addWatchList(self.settings['watchList'])

    # communityTreeView
    self.communityTreeView = self.ui.communityTreeView
    self.communityTableModel = CommunityTableModel(self)
    self.communityTreeView.setModel(self.communityTableModel)
    self.communityTreeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
    self.communityTreeView.setColumnWidth(0, 80)
    self.communityTreeView.setSortingEnabled(True)
    self.communityTreeView.setRootIsDecorated(False)
    self.communityTreeView.setAlternatingRowColors(True)
    self.communityTableModel.addCommunityList(self.settings['communityList'])

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

  def addWatchList(self, category, title, view_title):
    key = '%s%s' % (category, title)
    i = {key: {'category': category,
               'title': title,
               'view_title': view_title}}
    self.watchListTableModel.addWatchList(i)
    self.settings['watchList'].update(i)
    self.saveSettings()

  def addCommunity(self, com_id, com_name):
    u = {com_id: {'name': com_name}}
    self.communityTableModel.addCommunityList(u)
    self.settings['communityList'].update(u)
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
