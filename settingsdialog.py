#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

class SettingsDialog(QtGui.QDialog):
  def __init__(self, parent = None):
    QtGui.QDialog.__init__(self, parent)

    self.setWindowModality(QtCore.Qt.ApplicationModal)
    self.resize(300, 100)
    self.setWindowTitle(self.trUtf8('設定ウィンドウ'))

    layout = QtGui.QVBoxLayout(self)
    settingsLayout = QtGui.QGridLayout()

    browserOpenModeLabel = QtGui.QLabel(self)
    browserOpenModeLabel.setText(self.trUtf8('ブラウザでの開き方(Windows以外)'))
    settingsLayout.addWidget(browserOpenModeLabel, 0, 0)

    browserOpenModeComboBox = QtGui.QComboBox(self)
    browserOpenModeComboBox.addItem(self.trUtf8('同じウィンドウ'))
    browserOpenModeComboBox.addItem(self.trUtf8('新しいウィンドウ'))
    browserOpenModeComboBox.addItem(self.trUtf8('新しいタブ'))
    settingsLayout.addWidget(browserOpenModeComboBox, 0, 1)

    browserOpenModeLabel.setBuddy(browserOpenModeComboBox)

    pollingDurationLabel = QtGui.QLabel(self)
    pollingDurationLabel.setText(self.trUtf8('情報取得頻度'))
    settingsLayout.addWidget(pollingDurationLabel, 1, 0)

    pollingDurationComboBox = QtGui.QComboBox(self)
    pollingDurationComboBox.addItem(self.trUtf8('まめ'))
    pollingDurationComboBox.addItem(self.trUtf8('それなり'))
    pollingDurationComboBox.addItem(self.trUtf8('たまに'))
    settingsLayout.addWidget(pollingDurationComboBox, 1, 1)

    pollingDurationLabel.setBuddy(pollingDurationComboBox)

    layout.addLayout(settingsLayout)

    # Cancel/OK
    bb = QtGui.QDialogButtonBox(self)
    bb.setGeometry(QtCore.QRect(30, 50, 241, 32))
    bb.setOrientation(QtCore.Qt.Horizontal)
    bb.setStandardButtons(QtGui.QDialogButtonBox.Cancel |
                          QtGui.QDialogButtonBox.Ok)

    layout.addWidget(bb)

    self.connect(bb, QtCore.SIGNAL('accepted()'), lambda: self.settingsDialogAccepted())
    self.connect(bb, QtCore.SIGNAL('rejected()'), self.reject)

    self.browserOpenModeComboBox = browserOpenModeComboBox
    self.pollingDurationComboBox = pollingDurationComboBox
    self.show()

  def load(self, mainWindow):
    self.mainWindow = mainWindow
    self.settings = mainWindow.settings
    self.browserOpenModeComboBox.setCurrentIndex(self.settings['browserOpenMode'])

  def settingsDialogAccepted(self):
    changed = False
    if self.settings['browserOpenMode'] != self.browserOpenModeComboBox.currentIndex:
      self.settings['browserOpenMode'] = self.browserOpenModeComboBox.currentIndex()
      changed = True

    if changed:
      self.mainWindow.saveSettings()
    #self.pollingDurationComboBox = pollingDurationComboBox
    self.accept()
