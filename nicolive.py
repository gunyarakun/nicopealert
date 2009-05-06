# -*- coding: utf-8 -*-

# ニコ生クラス

import re
import urllib2
from BeautifulSoup import BeautifulSoup

class NicoLive:
  
  TABS = ['common', 'try', 'live', 'req', 'r18']
  WATCH_URL_REGEX = re.compile(r'(http://live.nicovideo.jp)?/watch/lv(\d+)')
  
  def __init__(self):
    pass

  def fetch_lives(self):
    id_set = set()
    for tab in self.TABS:
      url = 'http://live.nicovideo.jp/recent?tab=%s&p=1' % tab
      self.fetch_live_ids_from_html(url, id_set)
    print id_set

  def fetch_live_ids_from_html(self, url, id_set):
    opener = urllib2.build_opener()
    html = opener.open(url).read()
    soup = BeautifulSoup(html)
    
    for a in soup.findAll('a', href=self.WATCH_URL_REGEX):
      m = self.WATCH_URL_REGEX.match(a['href'])
      if m:
        id_set.add(int(m.group(2)))
