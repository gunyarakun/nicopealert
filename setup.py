#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import os
import sys
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
      version = '0.0.1',
      description = 'nicopedia/nicolive alerter',
      executables = [exe],
      options = {
        'build_exe': {
          'includes': ['sip',
                       'gzip',
                       'encodings.utf_8',
                       'encodings.ascii'],
          'include_files': [('dic.ico', 'dic.ico'),
                            ('live.ico', 'live.ico'),
                            ('event.wav', 'event.wav')],
        },
        'bdist_wininst': {
          'title': 'nicopealert',
          'bitmap': os.path.join('data', 'wininst_logo.bmp'),
        }
      })
