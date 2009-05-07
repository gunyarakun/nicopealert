#!/usr/bin/local/python
# -*- coding: utf-8 -*-

# ニコニコ大百科用アラートツール
# by Tasuku SUENAGA (a.k.a gunyarakun)

# TODO: nicoliveタイマー取得
# TODO: nicoliveいらないもの処理GC

from PyQt4 import QtCore, QtGui
from ui_mainwindow import Ui_MainWindow
from nicolive import NicoLive

class NicoLiveTreeNode:
   def __init__(self, data, parent = None):
     self.data = data
     self.parent = parent
     self.children = []

   def addChild(self, data):
     node = NicoLiveTreeNode(data, self)
     self.children.append(node)
     return node

   def row(self):
     if self.parent:
       return self.parent.children.index(self)
     else:
       return 0

class NicoLiveTreeViewModel(QtGui.QStandardItemModel):
  import re

  RE_LF = re.compile(r'\r?\n')

  COL_NAMES = [u'タイトル', u'コミュ名', u'生主', u'説明文']
  COL_KEYS = ['live_id_str', 'com_text', 'nusi', 'desc']

  def __init__(self, parent = None):
    QtGui.QStandardItemModel.__init__(self, 0, 4, parent)
    # set header
    for i, c in enumerate(self.COL_NAMES):
      self.setHeaderData(i, QtCore.Qt.Horizontal, QtCore.QVariant(c))

    nl = NicoLive()
    nl.fetch_lives()

    self.setRowCount(len(nl.live_details))

    for i, l in enumerate(nl.live_details.keys()):
      for j, k in enumerate(self.COL_KEYS):
        item = QtGui.QStandardItem()
        str = self.RE_LF.sub('', nl.live_details[l][k])
        # FIXME: str() for nicolive id
        item.setData(QtCore.QVariant(QtCore.QString(str)),
                     QtCore.Qt.DisplayRole)
        self.setItem(i, j, item)

class MainWindow(QtGui.QMainWindow):
  def __init__(self):
    QtGui.QDialog.__init__(self)

    self.ui = Ui_MainWindow()
    self.ui.setupUi(self)

    self.liveTreeView = self.ui.liveTreeView
    liveTreeViewModel = NicoLiveTreeViewModel(self)
    self.liveTreeView.setModel(liveTreeViewModel)

    self.connect(self.ui.pushButton, QtCore.SIGNAL('clicked()'),
                 self.accept)

  def accept(self):
    nl = NicoLive()
    nl.fetch_lives()

if __name__ == '__main__':
  import sys
  import codecs # for debug

  app = QtGui.QApplication(sys.argv)
  mw = MainWindow()
  mw.show()
  sys.exit(app.exec_())
