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
from datetime import datetime

# polling sucks, but...


class NicoPoll:

  # 生放送詳細情報を取得するキューサイズ
  # 枠全体よりは上が望ましいか
  MAX_LIVE_DETAIL_QUEUE_SIZE = 512
  # queueのタイムアウト
  QUEUE_BLOCK_TIMEOUT = 5

  # 詳細情報取得待ちの生放送idリスト
  liveid_queued_set = set()
  # 生放送詳細情報
  live_details = {}
  # 詳細情報取得待ち生放送idキュー
  live_detail_fetch_queue = Queue.Queue(MAX_LIVE_DETAIL_QUEUE_SIZE)

  def __init__(self, event_callback):
    self.opener = urllib2.build_opener()
    self.fetch_thread = threading.Thread(target = self.fetch_live_detail_from_queue)
    self.fetch_thread.start()
    self.event_callback = event_callback

  # not thread safe
  def fetch(self):
    url = 'http://dic.nicovideo.jp:2525/nicopealert.json.gz'
    print "fetch all"
    try:
      jsongz = self.opener.open(url).read()
      jsonstr = zlib.decompress(jsongz)
      events = json.JSONDecoder().decode(jsonstr)

      current_lives = events['lives']
      self.event_callback('current_lives', current_lives)

      for live_id, live_count in current_lives.items():
        if self.live_details.has_key(live_id):
          self.live_details[live_id]['watcher_count'] = live_count['watcher_count']
          self.live_details[live_id]['comment_count'] = live_count['comment_count']
        elif not live_id in self.liveid_queued_set:
          while True:
            try:
              self.live_detail_fetch_queue.put(live_id)
              self.liveid_queued_set.add(live_id)
              break
            except Queue.Full, e:
              # TODO: error handling
              time.sleep(1)
    except zlib.error:
      pass
    except:
      pass

  def fetch_live_detail_from_queue(self):
    opener = urllib2.build_opener()
    while 1:
      try:
        live_id = self.live_detail_fetch_queue.get(False) # non-blocking
        self.liveid_queued_set.discard(live_id)
        detail = self.fetch_live_detail_from_live_id(live_id, opener)
        if detail:
          self.live_details[live_id] = detail
          self.event_callback('live', {'live_id': live_id})
        else:
          self.live_detail_fetch_queue.put(live_id, True, self.QUEUE_BLOCK_TIMEOUT)
          self.liveid_queued_set.add(live_id)
        time.sleep(0.1)
      except Queue.Empty:
        # TODO: error handling
        time.sleep(2)

  def fetch_live_detail_from_live_id(self, live_id, opener):
    url = 'http://dic.nicovideo.jp:2525/%s.json.gz' % live_id.encode('ascii')
    print "fetch url:%s" % url
    try:
      jsongz = opener.open(url).read()
      jsonstr = zlib.decompress(jsongz, 15, 65535)

      detail = json.JSONDecoder().decode(jsonstr)

      # ちょっと加工
      detail['live_id'] = live_id
      print type(detail['time'])
      detail['time'] = datetime.fromtimestamp(detail['time'])
      return detail
    except urllib2.HTTPError, e:
      print "fetch %s error !!!!! : %s" % (live_id, e.message)
      return None
    except zlib.error, e:
      print "%s zlib extract error !!!!! : %s" % (live_id, e.message)
      return None
