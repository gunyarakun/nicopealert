# -*- coding: utf-8 -*-

# TODO: 再キューを行ったカウントを取得し、ある回数を超えたら再キューをやめる

import re
import urllib2
import Queue
import threading
import time # for sleep
import bz2
import StringIO
import json
from datetime import datetime

from version import VERSION

# polling sucks, but...

class NicoPoll:

  # 生放送詳細情報を取得するキューサイズ
  # 枠全体よりは上が望ましいか
  MAX_LIVE_DETAIL_QUEUE_SIZE = 512
  # queueのタイムアウト
  QUEUE_BLOCK_TIMEOUT = 5
  # fetchエラー数がこの数超えたら詳細情報は取得しない
  FETCH_ERROR_THRESHOLD = 8

  def __init__(self, dicTableModel, liveTableModel):
    self.opener = urllib2.build_opener()
    self.fetch_thread = threading.Thread(target = self.fetch_live_detail_from_queue)
    self.dicTableModel = dicTableModel
    self.liveTableModel = liveTableModel
    self.first = True
    self.fetch_feed_lock = threading.Lock()
    self.max_timestamp = 0

    # 詳細情報取得待ちの生放送idリスト
    self.liveid_queued_set = set()
    # 生放送詳細情報
    self.live_details = {}
    # 大百科詳細情報
    self.dic_details = {}

    # 詳細情報取得待ち生放送idキュー
    self.live_detail_fetch_queue = Queue.Queue(self.MAX_LIVE_DETAIL_QUEUE_SIZE)
    # fetch errorのカウント。
    self.fetch_error_count = {}

    # Modelからpollerへのアクセス
    dicTableModel.details = self.dic_details
    liveTableModel.details = self.live_details

    # 最後にThread開始
    self.fetch_thread.start()

  def fetch(self, mainWindow):
    self.fetch_feed_lock.acquire()
    try:
      first = self.first
      if first:
        url = 'http://dic.nicovideo.jp:2525/nicopealert-full.json.bz2'
      else:
        url = 'http://dic.nicovideo.jp:2525/nicopealert.json.bz2'

      while True:
        events = self.fetch_json_bz2(self.opener, url)
        if events is None:
          return
        if events['timestamp'] > self.max_timestamp:
          self.max_timestamp = events['timestamp']
          break
        time.sleep(5)

      self.first = False

      if events['version'] > VERSION:
        mainWindow.showVersionUpDialog()

      self.check_new_dic_events(events)
      current_lives = events['lives']
      self.liveTableModel.current_lives(current_lives)

      if first:
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
    finally:
      self.fetch_feed_lock.release()

  def dic_event_key(event):
    return '%s/%s:'

  CATEGORY_STR = {
    u'a': u'単語',
    u'v': u'動画',
    u'i': u'商品',
    u'u': u'ユーザ',
    u'c': u'コミュ',
  }

  def check_new_dic_events(self, events):
    # UNIX timeをPythonの時刻にする
    fetched_events = {}
    for p in events['pages']:
      p[u'time'] = datetime.fromtimestamp(p[u'time'])
      p[u'category_str'] = self.CATEGORY_STR[p[u'category']]
      p[u'type_str'] = u'編集'
      key = u'/r/%s/%s/%d' % (p[u'category'], p[u'title'], p[u'rev_id'])
      p[u'dic_id'] = key
      fetched_events[key] = p
    for r in events['reses']:
      r[u'time'] = datetime.fromtimestamp(r[u'time'])
      r[u'category_str'] = self.CATEGORY_STR[r[u'category']]
      if r.has_key(u'oekaki_id'):
        r[u'type_str'] = u'絵'
      elif r.has_key(u'mml_id'):
        r[u'type_str'] = u'ピコ'
      else:
        r[u'type_str'] = u'レス'
      key = u'/b/%s/%s/%d' % (r[u'category'], r[u'title'], r[u'res_no'])
      r[u'dic_id'] = key
      fetched_events[key] = r

    # 前回のと違うイベントだけをTableViewに通知
    new_keys = set(fetched_events.keys()) - set(self.dic_details.keys())
    new_events = {}
    for k in new_keys:
      new_events[k] = fetched_events[k]

    self.dic_details.update(fetched_events) # 先に代入
    self.dicTableModel.appendItems(new_events)

  def fetch_live_detail_from_queue(self):
    opener = urllib2.build_opener()
    while 1:
      try:
        live_id = self.live_detail_fetch_queue.get(False) # non-blocking
        self.fetch_live_detail_from_live_id(live_id, opener)
        time.sleep(0.5)
      except Queue.Empty:
        # TODO: error handling
        time.sleep(2)

  def add_live_details(self, details):
    for live_id, detail in details.items():
      detail[u'live_id'] = live_id
      detail[u'time'] = datetime.fromtimestamp(detail[u'time'])
    self.live_details.update(details)
    self.liveTableModel.appendItems(details)

  def fetch_json_bz2(self, opener, url):
    # print "fetch url:%s" % url
    try:
      jsonbz2 = opener.open(url).read()
      jsonstr = bz2.decompress(jsonbz2)

      return json.JSONDecoder().decode(jsonstr)
    except urllib2.HTTPError, e:
      print "*http fetch error* url: %s code: %d" % (url, e.code)
      return None
    except urllib2.URLError, e:
      # ニコニコ大百科json配信サーバにつなげない
      # 10分寝る
      time.sleep(600)
      print "*http url error* url: %s reason: %s" % (url, e.reason)
      return None
    except Exception, e:
      print "*bzip2 extract error* url: %s message: %s" % (url, str(e))
      return None

  def fetch_live_detail_from_live_id(self, live_id, opener):
    url = 'http://dic.nicovideo.jp:2525/%s.json.bz2' % live_id.encode('ascii')
    detail = self.fetch_json_bz2(opener, url)
    if detail:
      self.add_live_details({live_id: detail})
      self.liveid_queued_set.discard(live_id)
    else:
      if not self.fetch_error_count.has_key(live_id):
        self.fetch_error_count[live_id] = 0
      self.fetch_error_count[live_id] += 1
      if self.fetch_error_count[live_id] > self.FETCH_ERROR_THRESHOLD:
        print 'live detail fetch failed for %s.' % live_id
        self.liveid_queued_set.discard(live_id)
      else:
        # requeue
        self.live_detail_fetch_queue.put(live_id, True, self.QUEUE_BLOCK_TIMEOUT)
