#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import os
import sys
from version import VERSION
from distutils.core import setup
import py2exe
import sys, os

origIsSystemDLL = py2exe.build_exe.isSystemDLL
def isSystemDLL(pathname):
  if os.path.basename(pathname).lower() in ('msvcp90.dll'):
    return 0
  return origIsSystemDLL(pathname)
py2exe.build_exe.isSystemDLL = isSystemDLL

setup(
  name = 'nicopealert',
  version = VERSION,
  description = 'nicopedia/nicolive alerter',
  options = {
    'py2exe': {
      'compressed': 1,
      'optimize': 2,
      'bundle_files': 3,
      'packages': [
        'sip',
        'gzip',
        'encodings.utf_8',
        'encodings.cp932',
        'encodings.ascii',
        'encodings.idna',
        'encodings.raw_unicode_escape',
      ],
    }
  },
  console = [
    {
      'script': 'nicopealert.py',
      'icon_resources': [(1, 'dic.ico')],
      'company_name': 'Tasuku SUENAGA a.k.a. gunyarakun',
      'copyright': '2009- Tasuku SUNEAGA a.k.a. gunyarakun',
      # 'other_resources': [(24, 1, manifest)],
      'version': VERSION,
    },
  ],
  data_files = [
    ('', ['event.wav']),
    ('imageformats', [
      'imageformats/qico4.dll',
      'imageformats/qmng4.dll',
      'imageformats/qjpeg4.dll',
    ])
  ],
)
