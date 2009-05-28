#!/usr/bin/python
# -*- coding: utf-8 -*-

# ニコニコ大百科用アラートツール
# by Tasuku SUENAGA (a.k.a. gunyarakun)

# TODO: サーバクライアント、feedにバージョン情報とURLを入れる。
# TODO: バージョン情報は必ず読める形式にする。
# TODO: あるバージョン以下は強制起動禁止
# TODO: サーバサイド、終わった生放送が出続ける
# TODO: update URLの表示機能。
# TODO: 生放送タブのstretchポリシー見直し
# TODO: 検索条件の保存
# TODO: 新着イベントでタブ色変更
# TODO: 大百科古いイベント削除
# TODO: エラーハンドリング丁寧に、エラー報告ツール(ログとか) import logging
# TODO: ネットワーク無効実験
# TODO: Macでの動作確認、パッケージング
# TODO: *** リリースへの壁 ***
# TODO: timer_handlerのスレッド化。詰まることがあるかもしれないので。
# TODO: 生ごとの詳細表示
# TODO: リファクタリング
# TODO: コミュ・ウォッチリスト対象の背景色変更
# TODO: カラム移動・サイズの記憶
# TODO: タブのD&Dによる順番入れ替え
# TODO: 生放送タブのフリッカー防止

import os # for os.rename
import cPickle as pickle
import threading # for semaphore check
from PyQt4 import QtCore, QtGui
from ui_mainwindow import Ui_MainWindow

from nicopoll import NicoPoll
from usertab import *
from models import *

class MainWindow(QtGui.QMainWindow):
  POLLING_DURATION = 10000 # 10000msec = 10sec
  SETTINGS_FILE_NAME = 'nicopealert.dat'

  def checkSemaphore(self):
    self.sem = QtCore.QSystemSemaphore('nicopealert-app', 1)
    self.sem.acquire()
    self.firstApp = True
    self.inited = False

  def __init__(self, app):
    self.firstApp = False

    t = threading.Thread(target = self.checkSemaphore)
    t.start()
    t.join(0.2)

    if not self.firstApp:
      sys.exit(1)

    QtGui.QDialog.__init__(self)
    self.app = app

    self.ui = Ui_MainWindow()
    self.ui.setupUi(self)

    # load settings
    try:
      f = open(self.SETTINGS_FILE_NAME, 'rb')
      self.settings = pickle.load(f)
      f.close()
      self.settings['watchList']
      self.settings['communityList']
    except:
      self.settings = {'watchList': {},
                       'communityList': {}}

    # models
    self.dicTableModel = NicoDicTableModel(self)
    self.liveTableModel = NicoLiveTableModel(self)
    self.watchListTableModel = WatchListTableModel(self)
    self.communityListTableModel = CommunityTableModel(self)

    # tab widget
    self.tabWidget = QtGui.QTabWidget(self.ui.centralwidget)
    self.tabWidget.setLayoutDirection(QtCore.Qt.LeftToRight)
    self.ui.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)

    # initial tabs
    DicUserTabWidget(self)
    LiveUserTabWidget(self)
    WatchListUserTabWidget(self)
    CommunityListUserTabWidget(self)
    self.tabWidget.setCurrentIndex(0)

    # trayIcon/trayIconMenu/trayIconImg
    self.trayIconImg = QtGui.QIcon(self.tr(':/dic.ico'))
    self.trayIconMenu = QtGui.QMenu(self)
    self.trayIconMenu.addAction(u'終了', lambda: self.app.quit())
    self.trayIcon = QtGui.QSystemTrayIcon(self)
    self.trayIcon.setContextMenu(self.trayIconMenu)
    self.trayIcon.setIcon(self.trayIconImg)
    self.trayIcon.show()
    self.connect(self.trayIcon, QtCore.SIGNAL('activated(QSystemTrayIcon::ActivationReason)'), self.trayIconHandler)

    # first data fetch
    self.nicopoll = NicoPoll(self.dicTableModel,
                             self.liveTableModel)
    self.nicopoll.fetch()

    # set timer for polling
    self.timer = QtCore.QTimer(self)
    self.connect(self.timer, QtCore.SIGNAL('timeout()'), self.timer_handler)
    self.timer.setInterval(self.POLLING_DURATION)
    self.timer.start()

    # window style
    self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowMinimizeButtonHint)

  def show(self):
    QtGui.QMainWindow.show(self)
    self.activateWindow()

    if not self.inited:
      # タブの見た目関係初期化
      for i in xrange(0, self.tabWidget.count()):
        w = self.tabWidget.widget(i)
        w.init_after_show()

      # データ挿入
      self.watchListTableModel.appendItems(self.settings['watchList'])
      self.communityListTableModel.appendItems(self.settings['communityList'])

      self.inited = True

  def timer_handler(self):
    self.nicopoll.fetch()

  def trayIconHandler(self, reason):
    if reason == QtGui.QSystemTrayIcon.Trigger:
      if self.isVisible():
        self.hide()
      else:
        self.show()

  def appendWatchList(self, category, title, view_title):
    key = u'/%s/%s' % (category, title)
    i = {'category': category,
         'title': title,
         'view_title': view_title}
    self.watchListTableModel.appendItems({key: i})
    self.settings['watchList'][key] = i
    self.saveSettings()

  def appendCommunityList(self, com_id, com_name):
    # NOTE: com_idはkeyにもvalueにも入っている。
    u = {'id': com_id, 'name': com_name}
    self.communityListTableModel.appendItems({com_id: u})
    self.settings['communityList'][com_id] = u
    self.saveSettings()

  # NOTE: 小汚い
  def removeWatchList(self, row):
    category, title = \
      map(lambda d: unicode(d.toString()),
          self.watchListTableModel.raw_row_data(row)[0:2])
    key = u'%s%s' % (category, title)
    self.watchListTableModel.removeRow(row)
    del self.settings['watchList'][key]
    self.saveSettings()

  # NOTE: 小汚い
  def removeCommunityList(self, row):
    com_id = unicode(self.communityListTableModel.raw_row_data(row)[
        self.communityListTableModel.COL_COM_ID_INDEX].toString())
    self.communityListTableModel.removeRow(row)
    del self.settings['communityList'][com_id]
    self.saveSettings()

  def saveSettings(self):
    try:
      tmpfilename = self.SETTINGS_FILE_NAME + '.tmp' 
      f = open(tmpfilename, 'wb')
      pickle.dump(self.settings, f)
      f.close()
      if os.name == 'nt':
        try:
          os.remove(self.SETTINGS_FILE_NAME)
        except:
          pass
      os.rename(tmpfilename, self.SETTINGS_FILE_NAME)
    except:
      pass

  def closeEvent(self, event):
    # ×ボタンで、タスクトレイバーのみになる
    self.hide()
    event.ignore()

if __name__ == '__main__':
  import sys
  import codecs # for debug

  app = QtGui.QApplication(sys.argv)
  mw = MainWindow(app)
  try:
    mw.show()
    ret = app.exec_()
  finally:
    mw.trayIcon.hide()
    mw.sem.release()
  sys.exit(ret)
