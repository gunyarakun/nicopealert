#!/usr/bin/python
# -*- coding: utf-8 -*-

# ニコニコ大百科用アラートツール
# by Tasuku SUENAGA (a.k.a. gunyarakun)

# TODO: セーブデータjson化/cPickleやめとく
# TODO: セーブデータにバージョン入れる。
# TODO: browser.openの引数を設定できるように。
# TODO: 詳細画面の有無を設定できるように。
# TODO: ニコ生情報を更新しないように設定できるように。
# TODO: polling間隔を設定できるように。
# TODO: 開始時刻の幅をインタラクティブにする。
# TODO: TreeView幅見直す
# TODO: リスト登録時に記事情報・コミュ情報の取得
# TODO: リスト内記事情報・コミュ情報の更新
# TODO: コミュ画像のキャッシュ
# TODO: 時間って、何分前とかのほうがよくない？
# TODO: py2exe, py2appでのimageformatsディレクトリ自動検出
# TODO: py2exe、w9xpopen.exeいらない。
# TODO: サーバサイド、終わった生放送が出続ける
# TODO: 大百科古いイベント削除
# TODO: ネットワーク無効実験
# TODO: Macでの動作確認、パッケージング
# TODO: *** リリースへの壁 ***
# TODO: timer_handlerのスレッド化。詰まることがあるかもしれないので。
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

import sys
import codecs # for debug

from nicopoll import NicoPoll
from usertab import *
from models import *
from errorlogger import *

class DraggableTabBar(QtGui.QTabBar):
  def __init__(self, parent = None):
    QtGui.QTabBar.__init__(self, parent)
    self.setAcceptDrops(True)
    self.dragStartPos = None

  def mousePressEvent(self, event):
    if event.button() == QtCore.Qt.LeftButton:
      self.dragStartPos = QtCore.QPoint(event.pos())
    QtGui.QTabBar.mousePressEvent(self, event)

  def mouseMoveEvent(self, event):
    if not (event.buttons() & QtCore.Qt.LeftButton):
      return
    if (event.pos() - self.dragStartPos).manhattanLength() < \
        QtGui.QApplication.startDragDistance():
      return

    drag = QtGui.QDrag(self)
    mimeData = QtCore.QMimeData()
    mimeData.setData('action', 'tab-reordering')
    drag.setMimeData(mimeData)
    drag.exec_()

  def dragEnterEvent(self, event):
    m = event.mimeData()
    formats = m.formats()
    if formats.contains('action') and m.data('action') == 'tab-reordering':
      event.acceptProposedAction()

  def dropEvent(self, event):
    fromIndex = self.tabAt(self.dragStartPos)
    toIndex = self.tabAt(event.pos())

    if fromIndex != toIndex:
      self.emit(QtCore.SIGNAL('tabMoveRequested(int, int)'), fromIndex, toIndex)
    event.acceptProposedAction()

class DraggableTabWidget(QtGui.QTabWidget):
  def __init__(self, parent = None):
    QtGui.QTabWidget.__init__(self, parent)
    tabBar = DraggableTabBar()
    self.connect(tabBar,
                 QtCore.SIGNAL('tabMoveRequested(int, int)'),
                 self.moveTab)
    self.setTabBar(tabBar)

  def moveTab(self, fromIndex, toIndex):
    w = self.widget(fromIndex)
    icon = self.tabIcon(fromIndex)
    text = self.tabText(fromIndex)

    self.removeTab(fromIndex)
    self.insertTab(toIndex, w, icon, text)
    self.setCurrentIndex(toIndex)

class MainWindow(QtGui.QMainWindow):
  POLLING_DURATION = 10000 # 10000msec = 10sec
  SETTINGS_FILE_NAME = 'nicopealert.dat'

  def checkSemaphore(self):
    self.sem = QtCore.QSystemSemaphore('nicopealert-app', 1)
    self.sem.acquire()
    self.firstApp = True
    self.inited = False

  def __init__(self, app, logger):
    # 同時に１起動制限
    self.firstApp = False

    t = threading.Thread(target = self.checkSemaphore)
    t.start()
    t.join(0.2)

    if not self.firstApp:
      sys.exit(1)

    # 初期化処理
    QtGui.QDialog.__init__(self)
    self.app = app
    self.logger = logger

    self.ui = Ui_MainWindow()
    self.ui.setupUi(self)

    # load settings
    try:
      f = open(self.SETTINGS_FILE_NAME, 'rb')
      self.settings = pickle.load(f)
      f.close()
      self.settings['watchList']
      self.settings['communityList']
      self.settings['tabList']
    except:
      self.settings = {'watchList': {},
                       'communityList': {},
                       'tabList': []}

    # models
    self.dicTableModel = NicoDicTableModel(self)
    self.liveTableModel = NicoLiveTableModel(self)
    self.watchListTableModel = WatchListTableModel(self)
    self.communityListTableModel = CommunityTableModel(self)

    # tab widget
    self.tabWidget = DraggableTabWidget(self.ui.centralwidget)
    self.tabWidget.setLayoutDirection(QtCore.Qt.LeftToRight)
    self.ui.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)
    self.connect(self.tabWidget, QtCore.SIGNAL('currentChanged(int)'), self.tabWidgetChangedHandler)

    # initial tabs
    DicUserTabWidget(self)
    LiveUserTabWidget(self)
    WatchListUserTabWidget(self)
    CommunityListUserTabWidget(self)
    self.tabWidget.setCurrentIndex(0)

    # trayIcon/trayIconMenu/trayIconImg
    self.trayIconImg = QtGui.QIcon(self.tr(':/dic.ico'))
    self.trayIconMenu = QtGui.QMenu(self)
    self.trayIconMenu.addAction(u'表示/非表示', lambda: self.toggleWindowVisibility())
    self.trayIconMenu.addAction(u'終了', lambda: self.app.quit())
    self.trayIcon = QtGui.QSystemTrayIcon(self)
    self.trayIcon.setContextMenu(self.trayIconMenu)
    self.trayIcon.setIcon(self.trayIconImg)
    self.trayIcon.show()
    self.connect(self.trayIcon, QtCore.SIGNAL('activated(QSystemTrayIcon::ActivationReason)'), self.trayIconHandler)

    # window style
    self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowMinimizeButtonHint)

    # first data fetch
    self.nicopoll = NicoPoll(self.dicTableModel,
                             self.liveTableModel)
    self.nicopoll.fetch(self)

    # menu
    self.fileMenu = QtGui.QMenu(self.ui.menubar)
    self.fileMenu.addAction(u'設定', lambda: self.showSettingsDialog())
    self.fileMenu.setTitle(self.trUtf8('ファイル'))
    self.ui.menubar.addAction(self.fileMenu.menuAction())

  def show(self):
    QtGui.QMainWindow.show(self)
    self.activateWindow()

    if not self.inited:
      # データ挿入
      self.watchListTableModel.appendItems(self.settings['watchList'])
      self.communityListTableModel.appendItems(self.settings['communityList'])
      for tabcond in self.settings['tabList']:
        if tabcond['class'] == u'DicUserTabWidget':
          t = DicUserTabWidget(self, False)
          t.setCond(tabcond)
        elif tabcond['class'] == u'LiveUserTabWidget':
          t = LiveUserTabWidget(self, False)
          t.setCond(tabcond)

      # タブの見た目関係初期化
      for i in xrange(0, self.tabWidget.count()):
        w = self.tabWidget.widget(i)
        w.init_after_show()

      self.inited = True

    # set timer for polling
    self.timer = QtCore.QTimer(self)
    self.connect(self.timer, QtCore.SIGNAL('timeout()'), self.timer_handler)
    self.timer.setInterval(self.POLLING_DURATION)
    self.timer.start()

  def timer_handler(self):
    self.nicopoll.fetch(self)

    # 

  def showVersionUpDialog(self):
    # クライアントバージョンが古い
    msg = QtGui.QMessageBox.critical(self,
        self.trUtf8('バージョンアップのお知らせ'),
        self.trUtf8('ニコ百アラートがバージョンアップしました。お使いのバージョンは今後利用できなくなります。お手数ですが、バージョンアップお願いいたします。'),
        self.trUtf8('ダウンロードページを開く'),
        self.trUtf8('終了する'))
    if msg == 0:
      import webbrowser
      webbrowser.open('http://dic.nicovideo.jp/nicopealert/')
    sys.exit(2)

  def toggleWindowVisibility(self):
    if self.isVisible():
      self.hide()
    else:
      self.show()

  def trayIconHandler(self, reason):
    # NOTE: Macではダメっぽい
    if reason == QtGui.QSystemTrayIcon.DoubleClick:
      self.toggleWindowVisibility()

  def tabWidgetChangedHandler(self, index):
    self.tabWidget.currentWidget().setTabNotify(False)

  def appendWatchList(self, category, title, view_title):
    key = u'%s%s' % (category, title)
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

  # 各タブの情報を保存する
  def saveTabs(self):
    tabList = []
    for i in xrange(0, self.tabWidget.count()):
      w = self.tabWidget.widget(i)
      # 初期タブ以外を保存
      if not w.initial:
        tabList.append(w.cond())
    self.settings['tabList'] = tabList
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

  def showSettingsDialog(self):
    dialog = QtGui.QDialog(self)
    dialog.setWindowModality(QtCore.Qt.ApplicationModal)
    dialog.resize(300, 100)
    dialog.setWindowTitle(self.trUtf8('設定ウィンドウ'))

    layout = QtGui.QVBoxLayout(dialog)
    settingsLayout = QtGui.QGridLayout()

    browserOpenModeLabel = QtGui.QLabel(dialog)
    browserOpenModeLabel.setText(self.trUtf8('ブラウザでの開き方'))
    settingsLayout.addWidget(browserOpenModeLabel, 0, 0)

    browserOpenModeComboBox = QtGui.QComboBox(dialog)
    browserOpenModeComboBox.addItem(self.trUtf8('同じウィンドウ'))
    browserOpenModeComboBox.addItem(self.trUtf8('新しいウィンドウ'))
    browserOpenModeComboBox.addItem(self.trUtf8('新しいタブ'))
    settingsLayout.addWidget(browserOpenModeComboBox, 0, 1)

    browserOpenModeLabel.setBuddy(browserOpenModeComboBox)

    pollingDurationLabel = QtGui.QLabel(dialog)
    pollingDurationLabel.setText(self.trUtf8('情報取得頻度'))
    settingsLayout.addWidget(pollingDurationLabel, 1, 0)

    pollingDurationComboBox = QtGui.QComboBox(dialog)
    pollingDurationComboBox.addItem(self.trUtf8('まめ'))
    pollingDurationComboBox.addItem(self.trUtf8('5分ごと'))
    pollingDurationComboBox.addItem(self.trUtf8('10分ごと'))
    settingsLayout.addWidget(pollingDurationComboBox, 1, 1)

    pollingDurationLabel.setBuddy(pollingDurationComboBox)

    layout.addLayout(settingsLayout)

    # Cancel/OK
    bb = QtGui.QDialogButtonBox(dialog)
    bb.setGeometry(QtCore.QRect(30, 50, 241, 32))
    bb.setOrientation(QtCore.Qt.Horizontal)
    bb.setStandardButtons(QtGui.QDialogButtonBox.Cancel |
                          QtGui.QDialogButtonBox.Ok)

    layout.addWidget(bb)

    self.connect(bb, QtCore.SIGNAL('accepted()'), lambda: self.settingsDialogAccepted(dialog))
    self.connect(bb, QtCore.SIGNAL('rejected()'), dialog.reject)

    dialog.show()

  def settingsDialogAccepted(self, dialog):
    dialog.accept()

if __name__ == '__main__':
  logger = ErrorLogger('nicopealert.log')
  ret = 1
  try:
    app = QtGui.QApplication(sys.argv)
    mw = MainWindow(app, logger)
    try:
      mw.show()
      ret = app.exec_()
    finally:
      mw.trayIcon.hide()
      mw.sem.release()
  except:
    logger.log_exception()
    raise
  finally:
    sys.exit(ret)
