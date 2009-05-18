# -*- coding: utf-8 -*-

# ニコ生クラス

# TODO: start/end timeを取得 -> GC

import re
import urllib2
import Queue
import threading
import time # for sleep
import zlib
import StringIO
import json

# polling sucks, but...


class NicoPoll:

  MAX_QUEUE_SIZE = 512                                  # 生放送詳細情報を取得するキューサイズ
                                                        # 枠全体よりは上が望ましいか
  QUEUE_BLOCK_TIMEOUT = 5

  liveid_set = set()                                    # 現在放送中の生放送idリスト
  liveid_queued_set = set()                             # 詳細情報取得待ちの生放送idリスト
  live_details = {}                                     # 生放送詳細情報
  live_detail_fetch_queue = Queue.Queue(MAX_QUEUE_SIZE) # 詳細情報取得待ち生放送idキュー

  def __init__(self, event_callback):
    self.opener = urllib2.build_opener()
    self.fetch_thread = threading.Thread(target = self.fetch_live_detail_from_queue)
    self.fetch_thread.start()
    self.event_callback = event_callback

  # not thread safe
  def fetch(self):
    url = 'http://dic.nicovideo.jp:2525/nicopealert.json.gz'
    print "fetch all"
    jsongz = self.opener.open(url).read()
    jsonstr = zlib.decompress(jsongz)
    events = json.JSONDecoder().decode(jsonstr)

    self.liveid_set = set(events['lives'])
    for live_id in self.liveid_set:
      if not live_id in self.liveid_queued_set and \
         not self.live_details.has_key(live_id):
        self.liveid_queued_set.add(live_id)
        while True:
          try:
            self.live_detail_fetch_queue.put(live_id, True, self.QUEUE_BLOCK_TIMEOUT)
            break
          except Queue.Full, e:
            # TODO: error handling
            time.sleep(1)

  def fetch_live_detail_from_queue(self):
    opener = urllib2.build_opener()
    while 1:
      try:
        live_id = self.live_detail_fetch_queue.get(False) # non-blocking
        detail = self.fetch_live_detail_from_live_id(live_id, opener)
        if detail:
          self.live_details[live_id] = detail
          self.event_callback({'live_id': live_id})
        time.sleep(0.1)
      except Queue.Empty:
        # TODO: error handling
        time.sleep(2)

  def fetch_live_detail_from_live_id(self, live_id, opener):
    url = 'http://dic.nicovideo.jp:2525/%s.json.gz' % live_id.encode('ascii')
    try:
      print "fetch url:%s" % live_id
      jsongz = opener.open(url).read()
      jsonstr = zlib.decompress(jsongz, 15, 65535)

      detail = json.JSONDecoder().decode(jsonstr)
      detail['live_id'] = live_id
      return detail
    except:
      return None