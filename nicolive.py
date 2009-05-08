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
  DATE_REGEX = re.compile(ur'\s*(\d+)年(\d+)月(\d+)日\s*(\d+)時(\d+)分.*')

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
    self.fetch_lives()
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

  @staticmethod
  def live_id_to_str(live_id):
    return 'lv' + str(live_id)

  def fetch_lives(self):
    for tab in self.TABS:
      self.fetch_live_ids_from_tab(tab, self.liveid_set)

  def fetch_live_ids_from_tab(self, tab, id_set):
    url = 'http://live.nicovideo.jp/recent?tab=%s&p=1' % tab
    htmlio = self.opener.open(url)
    html = etree.parse(htmlio, etree.HTMLParser())

    divs = html.findall('//div[@id="search_result"]/div')
    for div in divs:
      c = div.attrib['class']
      if c == 'uc' or c == 'cc':
        a = div.find('div[@class="left"]/a')
        m = self.WATCH_URL_REGEX.match(a.attrib['href'])
        if m:
          live_id = int(m.group(2))
          id_set.add(live_id)
          l = {}
          self.live_details[live_id] = l
          counts = div.findall('div[@class="left"]/p[@class="txt10"]/strong')
          l['watcher_count'] = int(''.join(counts[0].xpath('text()')))
          l['comment_count'] = int(''.join(counts[1].xpath('text()')))
          if c == 'cc':
            l['category'] = u'チャンネル生'
            l['with_face'] = False
          else:
            categories = div.xpath('div[@class="btn"]/span/text()')
            l['category'] = categories[0]
            l['with_face'] = '○' if len(categories) > 1 else '×'
          start_date_str = ''.join(div.xpath('div[@class="right"]/span[@class="start_time"]/text()'))
          m = self.DATE_REGEX.match(start_date_str)
          if m:
            l['start_date'] = '%s/%s/%s %s:%s' % (m.group(1), m.group(2), m.group(3),
                                                  m.group(4), m.group(5))
          l['tab'] = tab

  def fetch_live_detail_from_queue(self):
    while 1:
      try:
        live_id = self.live_detail_fetch_queue.get(False) # non-blocking
        detail = self.fetch_live_detail_from_live_id(live_id)
        if detail:
          self.live_details[live_id].update(detail)
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
    if tmdl is not None:
      try:
# TODO: 開始時間・来場者数・コメ数・コミュ限定・タグ・顔出し・アラート対象
        title = ''.join(html.xpath('//h2[@class="ttl"]/text()')).strip()
        desc = ''.join(tmdl.xpath('p[@class="stream_description"]/text()')).strip()
        nusi = ''.join(tmdl.xpath('p/span[@class="nicopedia"]/text()')).strip()
        com_a = tmdl.findall('p/a')[-1]
        com_url = com_a.attrib['href']
        com_id = com_url[com_url.rindex('/') + 1:]
        com_text = ''.join(com_a.xpath('text()')).strip()

        return {
          'live_id': live_id,
          'live_id_str': self.live_id_to_str(live_id),
          'title': title,
          'desc': desc,
          'nusi': nusi,
          'com_id': com_id,
          'com_text': com_text,
          'com_img_url': 'http://icon.nicovideo.jp/community/%s.jpg' % com_id,
        }
      except:
        print 'lv%d parse error' % live_id
    return None
