#!/usr/bin/local/python
# -*- coding: utf-8 -*-

# ニコニコ大百科用アラートツール
# by Tasuku SUENAGA (a.k.a gunyarakun)

from PyQt4 import QtCore, QtGui
from ui_mainwindow import Ui_MainWindow
from nicolive import NicoLive

class MainWindow(QtGui.QMainWindow):
  def __init__(self):
    QtGui.QDialog.__init__(self)
    
    self.ui = Ui_MainWindow()
    self.ui.setupUi(self)
    
    self.connect(self.ui.pushButton, QtCore.SIGNAL('clicked()'),
                 self.accept)
  def accept(self):
    nl = NicoLive()
    nl.fetch_lives()

if __name__ == '__main__':
  import sys
  app = QtGui.QApplication(sys.argv)
  mw = MainWindow()
  mw.show()
  sys.exit(app.exec_())
