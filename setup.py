#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import os
import sys
from version import VERSION
from cx_Freeze import setup, Executable

base = None
if sys.platform == 'win32':
  base = 'Win32GUI'

# NOTE: if follows cx_Freeze document.
#exe = Executable(script = 'nicopealert.py',
#                 includes = ['sip',
#                             'gzip',
#                             'encodings.utf_8',
#                             'encodings.ascii'],
#                 icon = 'dic.ico',
#                 base = base)
exe = Executable(script = 'nicopealert.py',
                 icon = 'dic.ico',
                 base = base)

setup(name = 'nicopealert',
      version = VERSION,
      description = 'nicopedia/nicolive alerter',
      executables = [exe],
      options = {
        'build_exe': {
          'includes': ['sip',
                       'gzip',
                       'encodings.utf_8',
                       'encodings.ascii'],
          'include_files': [('event.wav', 'event.wav'),
                            ('imageformats/qico4.dll',
                             'imageformats/qico4.dll')],
        },
        'bdist_wininst': {
          'title': 'nicopealert',
          'bitmap': os.path.join('data', 'wininst_logo.bmp'),
        }
      })
