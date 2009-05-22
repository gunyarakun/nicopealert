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

  # 大百科詳細情報
  dic_details = {}

  def __init__(self, dicTreeViewModel, liveTreeViewModel):
    self.opener = urllib2.build_opener()
    self.fetch_thread = threading.Thread(target = self.fetch_live_detail_from_queue)
    self.fetch_thread.start()
    self.dicTreeViewModel = dicTreeViewModel
    self.liveTreeViewModel = liveTreeViewModel
    self.first = True

  # not thread safe
  def fetch(self):
    if self.first:
      url = 'http://dic.nicovideo.jp:2525/nicopealert-full.json.gz'
    else:
      url = 'http://dic.nicovideo.jp:2525/nicopealert.json.gz'
    try:
      jsongz = self.opener.open(url).read()
      jsonstr = zlib.decompress(jsongz)
      events = json.JSONDecoder().decode(jsonstr)
    except urllib2.HTTPError, e:
      return
    except zlib.error:
      return

    self.check_new_dic_events(events)
    current_lives = events['lives']
    try:
      self.liveTreeViewModel.current_lives(current_lives)
    except:
      pass

    if self.first:
      self.add_live_details(current_lives)
    else:
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

  def dic_event_key(event):
    return '%s/%s:'

  def check_new_dic_events(self, events):
    # UNIX timeをPythonの時刻にする
    fetched_events = {}
    for p in events['pages']:
      p[u'time'] = datetime.fromtimestamp(p[u'time'])
      key = u'%s/%s/%d' % (p[u'category'], p[u'title'], p[u'rev_no'])
      fetched_events[key] = p
    for r in events['reses']:
      r[u'time'] = datetime.fromtimestamp(r[u'time'])
      key = u'%s/%s/%d' % (r[u'category'], r[u'title'], r[u'res_no'])
      fetched_events[key] = r

    # 前回のと違うイベントだけをTreeViewに通知
    new_keys = set(fetched_events.keys()) - set(self.dic_details.keys())
    new_events = []
    for k in new_keys:
      new_events.append(fetched_events[k])

    self.dicTreeViewModel.append_event(new_events)
    self.dic_details.update(fetched_events)

  def fetch_live_detail_from_queue(self):
    opener = urllib2.build_opener()
    while 1:
      try:
        live_id = self.live_detail_fetch_queue.get(False) # non-blocking
        self.liveid_queued_set.discard(live_id)
        detail = self.fetch_live_detail_from_live_id(live_id, opener)
        if detail:
          self.add_live_details({live_id: detail})
        else:
          self.live_detail_fetch_queue.put(live_id, True, self.QUEUE_BLOCK_TIMEOUT)
          self.liveid_queued_set.add(live_id)
        time.sleep(0.1)
      except Queue.Empty:
        # TODO: error handling
        time.sleep(2)

  def add_live_details(self, details):
    for live_id, detail in details.items():
      detail[u'live_id'] = live_id
      detail[u'time'] = datetime.fromtimestamp(detail[u'time'])
    self.live_details.update(detail)
    self.liveTreeViewModel.live_handler(details.values())

  def fetch_live_detail_from_live_id(self, live_id, opener):
    url = 'http://dic.nicovideo.jp:2525/%s.json.gz' % live_id.encode('ascii')
    # print "fetch url:%s" % url
    try:
      jsongz = opener.open(url).read()
      jsonstr = zlib.decompress(jsongz, 15, 65535)

      detail = json.JSONDecoder().decode(jsonstr)
      return detail
    except urllib2.HTTPError, e:
      print "fetch %s error !!!!! : %s" % (live_id, e.message)
      return None
    except zlib.error, e:
      print "%s zlib extract error !!!!! : %s" % (live_id, e.message)
      return None
