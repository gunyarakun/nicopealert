# -*- coding: utf-8 -*-

# ニコ生クラス

# TODO: start/end timeを取得 -> GC

import re
import urllib2
from lxml import etree
import Queue
import threading
import time # for sleep

class NicoLive:
  TABS = ['common', 'try', 'live', 'req', 'r18']
  WATCH_URL_REGEX = re.compile(r'(http://live.nicovideo.jp)?/watch/lv(\d+)')
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

  def fetch(self):
    self.fetch_lives()
    # add que to fetch live details.
    for live_id in self.liveid_set:
      if not self.live_details.has_key(live_id) \
         and not live_id in self.liveid_queued_set:
        self.liveid_queued_set.add(live_id)
        while True:
          try:
            self.live_detail_fetch_queue.put(live_id, True, self.QUEUE_BLOCK_TIMEOUT)
            break
          except Queue.Full, e:
            # TODO: error handling
            pass

  @staticmethod
  def live_id_to_str(live_id):
    return 'lv' + str(live_id)

  def fetch_lives(self):
    for tab in self.TABS:
      url = 'http://live.nicovideo.jp/recent?tab=%s&p=1' % tab
      self.fetch_live_ids_from_html(url, self.liveid_set)

  def fetch_live_ids_from_html(self, url, id_set):
    htmlio = self.opener.open(url)
    html = etree.parse(htmlio, etree.HTMLParser())

    for a in html.iter('a'):
      if a.attrib.has_key('href'):
        m = self.WATCH_URL_REGEX.match(a.attrib['href'])
        if m:
          id_set.add(int(m.group(2)))

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
    url = 'http://live.nicovideo.jp/watch/lv%d' % live_id
    htmlio = self.opener.open(url)
    html = etree.parse(htmlio, etree.HTMLParser())

    tmdl = html.find('//div[@class="tmdl"]')
    # tmdlの中は、詳細コメント・主・コミュニティ・注意書きの順で<p>が入ってる
    if tmdl is not None:
      try:
        title = ''.join(html.xpath('//h2[@class="ttl"]/text()')).strip()
        desc = ''.join(tmdl.xpath('p[@class="stream_description"]/text()')).strip()
        nusi = ''.join(tmdl.xpath('p/span[@class="nicopedia"]/text()')).strip()
        com_a = tmdl.findall('p/a')[-1]
        com_url = com_a.attrib['href']
        com_id = com_url[com_url.rindex('/') + 1:]
        com_text = ''.join(com_a.xpath('text()')).strip()

        return {'live_id': live_id,
                'live_id_str': self.live_id_to_str(live_id),
                'title': title,
                'desc': desc,
                'nusi': nusi,
                'com_id': com_id,
                'com_text': com_text}
      except:
        print 'lv%d parse error' % live_id
    return None
