# -*- coding: utf-8 -*-

# ニコ生クラス

# TODO: start/end timeを取得 -> GC

import re
import urllib2
import Queue
import threading
import time # for sleep
import gzip
import StringIO
import json

class NicoLive:
  MAX_QUEUE_SIZE = 512 # 枠全体よりは上が望ましいか
  QUEUE_BLOCK_TIMEOUT = 5

  liveid_set = set()
  liveid_queued_set = set()
  live_details = {}
  live_detail_fetch_queue = Queue.Queue(MAX_QUEUE_SIZE)

  def __init__(self, fetch_detail_callback):
    self.opener = urllib2.build_opener()
    self.fetch_thread = threading.Thread(target = self.fetch_live_detail_from_queue)
    self.fetch_thread.start()
    self.fetch_detail_callback = fetch_detail_callback

  # not thread safe
  def fetch(self):
    url = 'http://dic.nicovideo.jp:2525/nicopealert.json.gz'
    jsongz = self.opener.open(url).read()
    sio = StringIO.StringIO(jsongz)
    jsonstr = gzip.GzipFile(fileobj=sio).read()
    events = json.JSONDecoder().decode(jsonstr)

    self.liveid_set = set(events['lives'])
    # add que to fetch live details.
    for live_id in self.liveid_set:
      if not live_id in self.liveid_queued_set:
        self.liveid_queued_set.add(live_id)
        while True:
          try:
            self.live_detail_fetch_queue.put(live_id, True, self.QUEUE_BLOCK_TIMEOUT)
            break
          except Queue.Full, e:
            # TODO: error handling
            time.sleep(1)

  def fetch_live_detail_from_queue(self):
    while 1:
      try:
        live_id = self.live_detail_fetch_queue.get(False) # non-blocking
        detail = self.fetch_live_detail_from_live_id(live_id)
        if detail:
          self.live_details[live_id] = detail
          self.fetch_detail_callback(live_id)
        time.sleep(0.1)
      except Queue.Empty:
        # TODO: error handling
        time.sleep(2)

  def fetch_live_detail_from_live_id(self, live_id):
    url = 'http://dic.nicovideo.jp:2525/%s.json.gz' % live_id.encode('ascii')
    try:
      jsongz = self.opener.open(url).read()
      sio = StringIO.StringIO(jsongz)
      jsonstr = gzip.GzipFile(fileobj=sio).read()

      detail = json.JSONDecoder().decode(jsonstr)
      detail['live_id'] = live_id
      return detail
    except:
      return None
