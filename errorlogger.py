#!/usr/bin/python
# -*- coding: utf-8 -*-

# エラーロガー

import sys
import logging
import logging.handlers
import threading
import traceback

class ErrorLogger():
  def __init__(self, filename, max_traceback = 16):
    logger = logging.getLogger('nicopealert')
    handler = logging.handlers.RotatingFileHandler(
                 filename, maxBytes = 65536, backupCount = 2)
    logger.addHandler(handler)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)

    self.logger = logger
    self.max_traceback = max_traceback
    self.lock = threading.Lock()

  def log_exception(self):
    c, e, t = sys.exc_info()

    tbs = traceback.format_exception_only(c, e) + \
          traceback.format_tb(t, self.max_traceback)
    self.lock.acquire()
    try:
      for tb in tbs:
        for l in tb.split('\n'):
          if len(l) > 0:
            self.logger.error(l)
    finally:
      self.lock.release()
