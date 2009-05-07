# -*- coding: utf-8 -*-

# ニコ生クラス

# TODO: start/end timeを取得 -> GC

import re
import urllib2
from lxml import etree

class NicoLive:
  TABS = ['common', 'try', 'live', 'req', 'r18']
  WATCH_URL_REGEX = re.compile(r'(http://live.nicovideo.jp)?/watch/lv(\d+)')

  liveid_set = set()
  live_details = {}

  def __init__(self):
    self.opener = urllib2.build_opener()

  def fetch_lives(self):
    for tab in self.TABS:
      url = 'http://live.nicovideo.jp/recent?tab=%s&p=1' % tab
      self.fetch_live_ids_from_html(url, self.liveid_set)
    for live_id in self.liveid_set:
      if not self.live_details.has_key(live_id):
        detail = self.fetch_live_detail_from_live_id(live_id)
        if detail:
          self.live_details[live_id] = detail
      break

  def fetch_live_ids_from_html(self, url, id_set):
    htmlio = self.opener.open(url)
    html = etree.parse(htmlio, etree.HTMLParser())

    for a in html.iter('a'):
      if a.attrib.has_key('href'):
        m = self.WATCH_URL_REGEX.match(a.attrib['href'])
        if m:
          id_set.add(int(m.group(2)))

  def fetch_live_detail_from_live_id(self, live_id):
    url = 'http://live.nicovideo.jp/watch/lv%d' % live_id
    htmlio = self.opener.open(url)
    html = etree.parse(htmlio, etree.HTMLParser())

    tmdl = html.find('//div[@class="tmdl"]')
    # tmdlの中は、詳細コメント・主・コミュニティ・注意書きの順で<p>が入ってる
    if tmdl is not None:
      try:
        desc = ''.join(tmdl.xpath('p[@class="stream_description"]/text()')).strip()
        nusi = ''.join(tmdl.xpath('p/span[@class="nicopedia"]/text()')).strip()
        com_a = tmdl.findall('p/a')[-1]
        com_url = com_a.attrib['href']
        com_id = com_url[com_url.rindex('/') + 1:]
        com_text = ''.join(com_a.xpath('text()')).strip()

        return {'live_id': live_id,
                'live_id_str': 'lv' + str(live_id),
                'desc': desc,
                'nusi': nusi,
                'com_id': com_id,
                'com_text': com_text}
      except:
        print 'lv%d parse error' % live_id
    return None
